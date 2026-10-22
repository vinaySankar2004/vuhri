"""Build a stylised character from a design file, headless in Blender.

The design names the joints, the bones between them, and the body's shapes, each a smooth hull
around a few rounded blobs. The build makes the skeleton, shapes every part, fuses the parts
into one watertight mesh (voxel remesh), softens the joins, binds the mesh to the bones with
automatic weights, and saves a .blend. Left-side joints, bones and shapes (".L") are mirrored to
the right. The character stands at the origin, facing -Y, in Blender's metres.

With --check, it also renders a check sheet into a folder: front and side at rest, which bone
moves which part, and the test poses the design lists.

Usage:
  Blender -b --python build_character.py -- --design striker.json --out striker.blend
          [--check checks/striker]
"""

import argparse
import colorsys
import json
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector


def args_after_dashes():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", help="folder for the check renders")
    return ap.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def mirrored(design):
    """Add the right side: every .L joint, bone and shape, reflected across x = 0."""

    def flip(name):
        return name[:-2] + ".R" if isinstance(name, str) and name.endswith(".L") else name

    def flip_point(p):
        return flip(p) if isinstance(p, str) else [-p[0], p[1], p[2]]

    joints = dict(design["joints"])
    for name, (x, y, z) in design["joints"].items():
        if name.endswith(".L"):
            joints[flip(name)] = [-x, y, z]
    bones = list(design["bones"])
    bones += [[flip(n), flip(a), flip(b), flip(p)] for n, a, b, p in design["bones"] if n.endswith(".L")]
    shapes = list(design["shapes"])
    shapes += [
        {"name": flip(s["name"]), "blobs": [[flip_point(p), r] for p, r in s["blobs"]]}
        for s in design["shapes"]
        if s["name"].endswith(".L")
    ]
    return joints, bones, shapes


def linear(hex_colour: str):
    """sRGB hex to the linear RGBA Blender's materials expect."""
    c = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return (*[v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c], 1.0)


def build_rig(joints, bones):
    data = bpy.data.armatures.new("rig")
    rig = bpy.data.objects.new("rig", data)
    bpy.context.scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name, a, b, parent in bones:
        eb = data.edit_bones.new(name)
        eb.head, eb.tail = Vector(joints[a]), Vector(joints[b])
        if parent:
            eb.parent = data.edit_bones[parent]
            eb.use_connect = (eb.parent.tail - eb.head).length < 1e-6
    bpy.ops.object.mode_set(mode="OBJECT")
    return rig


def build_body(joints, shapes, voxel, soften):
    """Each shape is the convex hull of its blobs; the parts are then fused into one surface."""
    bm = bmesh.new()
    for shape in shapes:
        part = bmesh.new()
        for point, r in shape["blobs"]:
            centre = Vector(joints[point]) if isinstance(point, str) else Vector(point)
            rx, ry, rz = (r, r, r) if isinstance(r, (int, float)) else r
            bmesh.ops.create_uvsphere(
                part, u_segments=24, v_segments=12, radius=1.0,
                matrix=Matrix.Translation(centre) @ Matrix.Diagonal((rx, ry, rz, 1)),
            )
        bmesh.ops.convex_hull(part, input=part.verts[:], use_existing_faces=False)
        # Keep only the hull: drop the blobs' interior points the hull left behind.
        bmesh.ops.delete(part, geom=[v for v in part.verts if not v.link_faces], context="VERTS")
        me = bpy.data.meshes.new("part")
        part.to_mesh(me)
        part.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    me = bpy.data.meshes.new("body")
    bm.to_mesh(me)
    bm.free()
    body = bpy.data.objects.new("body", me)
    bpy.context.scene.collection.objects.link(body)

    fuse = body.modifiers.new("fuse", "REMESH")
    fuse.mode = "VOXEL"
    fuse.voxel_size = voxel
    smooth = body.modifiers.new("soften", "SMOOTH")
    smooth.factor, smooth.iterations = 0.5, soften
    solid = bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    body.modifiers.clear()
    old = body.data
    body.data = solid
    bpy.data.meshes.remove(old)
    solid.name = "body"
    return body


def bind(body, rig):
    """Automatic weights: Blender spreads each bone's pull over the body like heat."""
    for o in bpy.context.scene.objects:
        o.select_set(False)
    body.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    next(m for m in body.modifiers if m.type == "ARMATURE").use_deform_preserve_volume = True


def side_materials(body, colours):
    """Three slots: centre, left limbs, right limbs. A shot recolours whichever side is far."""
    groups = {g.index: g.name for g in body.vertex_groups}
    for slot in ("centre", "left", "right"):
        m = bpy.data.materials.new(slot)
        m.diffuse_color = linear(colours["body"])
        body.data.materials.append(m)
    side = []
    for v in body.data.vertices:
        w = {"L": 0.0, "R": 0.0, "C": 0.0}
        for e in v.groups:
            name = groups[e.group]
            w["L" if name.endswith(".L") else "R" if name.endswith(".R") else "C"] += e.weight
        side.append(max(w, key=w.get))
    for poly in body.data.polygons:
        votes = [side[i] for i in poly.vertices]
        top = max(set(votes), key=votes.count)
        poly.material_index = {"C": 0, "L": 1, "R": 2}[top]


# ---- Check renders -------------------------------------------------------------------------


def aim(rig, name, direction):
    """Point a bone along a world direction, turning everything below it."""
    pb = rig.pose.bones[name]
    m = rig.matrix_world @ pb.matrix
    now = (m.to_3x3() @ Vector((0, 1, 0))).normalized()
    turn = now.rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
    pivot = m.translation.copy()
    pb.matrix = rig.matrix_world.inverted() @ Matrix.Translation(pivot) @ turn @ Matrix.Translation(-pivot) @ m
    bpy.context.view_layer.update()


def pose(rig, bones, aims):
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    order = [b[0] for b in bones]  # parents come first in the design
    for name in sorted(aims, key=order.index):
        aim(rig, name, aims[name])


def shoot(scene, body, view, path, size=900):
    """Orthographic shot along `view`, framed on the posed body."""
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    pts = [body.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    view = Vector(view).normalized()
    up = Vector((0, 0, 1))
    right = view.cross(up).normalized()
    xs, zs = [p.dot(right) for p in pts], [p.z for p in pts]
    centre = right * (max(xs) + min(xs)) / 2 + up * (max(zs) + min(zs)) / 2
    cam = scene.camera
    cam.data.ortho_scale = max(max(xs) - min(xs), max(zs) - min(zs)) * 1.12
    cam.location = centre - view * 10
    cam.rotation_euler = view.to_track_quat("-Z", "Y").to_euler()
    scene.render.resolution_x = scene.render.resolution_y = size
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def bone_colours(body):
    """Colour each vertex by the bone that pulls it most, for a check of the weights."""
    me = body.data
    names = sorted({g.name for g in body.vertex_groups})
    hue = {n: (i * 0.61803) % 1 for i, n in enumerate(names)}
    attr = me.color_attributes.new("bones", "FLOAT_COLOR", "POINT")
    groups = {g.index: g.name for g in body.vertex_groups}
    for v in me.vertices:
        top = max(v.groups, key=lambda e: e.weight, default=None)
        if top is None:
            attr.data[v.index].color = (1, 0, 0, 1)
            continue
        r, g, b = colorsys.hsv_to_rgb(hue[groups[top.group]], 0.55, 0.9 * top.weight + 0.1)
        attr.data[v.index].color = (r, g, b, 1)
    me.color_attributes.active_color = attr


def check(design, bones, rig, body, folder):
    os.makedirs(folder, exist_ok=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.render_aa = "8"
    scene.view_settings.view_transform = "Standard"
    scene.render.film_transparent = False
    scene.world = bpy.data.worlds.new("plane")
    scene.world.color = linear(design["colours"]["background"])[:3]
    scene.render.image_settings.file_format = "PNG"
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = "ORTHO"
    scene.collection.objects.link(cam)
    scene.camera = cam
    pose(rig, bones, {})
    shoot(scene, body, (0, 1, 0), os.path.join(folder, "1-front.png"))
    # From the side, the figure's right faces this camera and its left limbs take the far colour.
    body.data.materials["left"].diffuse_color = linear(design["colours"]["far"])
    side = (1, 0, 0)
    shoot(scene, body, side, os.path.join(folder, "2-side.png"))
    for i, (name, aims) in enumerate(design.get("checkPoses", {}).items(), 4):
        pose(rig, bones, aims)
        shoot(scene, body, side, os.path.join(folder, f"{i}-{name}.png"))
    pose(rig, bones, {})
    bone_colours(body)
    scene.display.shading.color_type = "VERTEX"
    shoot(scene, body, side, os.path.join(folder, "3-weights.png"))
    scene.display.shading.color_type = "MATERIAL"
    body.data.color_attributes.remove(body.data.color_attributes["bones"])
    body.data.materials["left"].diffuse_color = linear(design["colours"]["body"])
    bpy.data.objects.remove(cam)


def main() -> None:
    a = args_after_dashes()
    design = json.load(open(a.design))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    joints, bones, shapes = mirrored(design)
    rig = build_rig(joints, bones)
    body = build_body(joints, shapes, design.get("voxel", 0.006), design.get("soften", 8))
    bind(body, rig)
    side_materials(body, design["colours"])
    body["farColour"] = design["colours"]["far"]  # a shot shades the far side's limbs with it
    if a.check:
        check(design, bones, rig, body, a.check)
    bpy.context.preferences.filepaths.save_version = 0  # no .blend1 backup beside it
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.out))
    print("BUILT", a.out, len(body.data.vertices), "vertices")


if __name__ == "__main__":
    main()
