"""Render a flat 2D character performing a recorded motion, headless in Blender.

Blender imports the BVH, dresses its skeleton in round-section limbs (so a limb's drawn width
never changes as it twists), frames it from the side the motion travels across, and renders a
transparent PNG sequence with flat, exact colours. A JSON sidecar records the frame and pixel
where the moving foot is fastest (a kick's contact), so the video can place a ball there.

Usage:
  Blender -b --python render_character.py -- --bvh clip.bvh --character striker.json
          --skeleton cmu --out renders/kick [--fps 60] [--size 1080] [--before 1.0] [--after 1.2]
"""

import argparse
import json
import math
import os
import sys

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))


def args_after_dashes():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bvh", required=True)
    ap.add_argument("--character", required=True)
    ap.add_argument("--skeleton", default="cmu")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--size", type=int, default=1080)
    ap.add_argument("--before", type=float, default=1.0, help="seconds before the peak")
    ap.add_argument("--after", type=float, default=1.2, help="seconds after the peak")
    ap.add_argument("--frames", help="explicit scene frame range a-b instead of the peak window")
    return ap.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def linear(hex_colour: str):
    """sRGB hex to the linear RGBA Blender's materials expect."""
    c = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return (*lin, 1.0)


def material(name: str, hex_colour: str):
    m = bpy.data.materials.new(name)
    m.diffuse_color = linear(hex_colour)
    return m


def mesh_object(name: str, build, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def cylinder(a: Vector, b: Vector, radius: float):
    axis = b - a
    rot = Vector((0, 0, 1)).rotation_difference(axis.normalized()).to_matrix().to_4x4()
    m = Matrix.Translation((a + b) / 2) @ rot

    def build(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=radius, radius2=radius, depth=axis.length, matrix=m)

    return build


def sphere(c: Vector, rx: float, ry: float, rz: float, align: Vector = None):
    rot = Matrix.Identity(4)
    if align is not None:
        rot = Vector((0, 0, 1)).rotation_difference(align.normalized()).to_matrix().to_4x4()
    m = Matrix.Translation(c) @ rot @ Matrix.Diagonal((rx, ry, rz, 1))

    def build(bm):
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0, matrix=m)

    return build


def attach(ob, arm, bone_name: str):
    """Parent to a bone so the shape, built at the rest pose, follows it exactly."""
    ob.parent = arm
    ob.parent_type = "BONE"
    ob.parent_bone = bone_name
    bpy.context.view_layer.update()
    ob.matrix_world = Matrix.Identity(4)


def main() -> None:
    a = args_after_dashes()
    character = json.load(open(a.character))
    skeleton = json.load(open(os.path.join(HERE, "skeletons.json")))[a.skeleton]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = a.fps
    bpy.ops.import_anim.bvh(
        filepath=a.bvh, axis_forward="-Z", axis_up="Y", global_scale=1.0,
        use_fps_scale=True, update_scene_fps=False, update_scene_duration=True,
    )
    arm = next(o for o in scene.objects if o.type == "ARMATURE")
    bones = arm.pose.bones

    def head(name):
        return arm.matrix_world @ bones[name].head

    def tail(name):
        return arm.matrix_world @ bones[name].tail

    # Measure the motion: which foot moves fastest, which way, and when.
    first, last = scene.frame_start, scene.frame_end
    track = {"left": [], "right": []}
    for f in range(first, last + 1):
        scene.frame_set(f)
        for side in track:
            track[side].append(tail(skeleton["limbs"][side]["toe"]).copy())
    best = (0.0, "right", first)
    for side, pts in track.items():
        for i in range(1, len(pts)):
            v = pts[i] - pts[i - 1]
            speed = Vector((v.x, v.y)).length
            if speed > best[0]:
                best = (speed, side, first + i)
    _, kick_side, peak = best
    k = peak - first
    vel = track[kick_side][min(k + 1, len(track[kick_side]) - 1)] - track[kick_side][max(k - 1, 0)]
    forward = Vector((vel.x, vel.y, 0)).normalized()

    if a.frames:
        start, end = (int(x) for x in a.frames.split("-"))
    else:
        start = max(first, peak - round(a.before * a.fps))
        end = min(last, peak + round(a.after * a.fps))

    # Build the body at the rest pose, then let the motion drive it.
    arm.data.pose_position = "REST"
    bpy.context.view_layer.update()
    height = tail(skeleton["head"]).z - min(head(skeleton["limbs"][s]["toe"]).z for s in ("left", "right"))
    w = {k2: v * height for k2, v in character["widths"].items()}
    view = Vector((0, 0, 1)).cross(forward)  # from the camera towards the figure
    left_near = (head(skeleton["limbs"]["left"]["hip"]) - head(skeleton["limbs"]["right"]["hip"])).dot(-view) > 0
    near = material("near", character["colors"]["near"])
    far = material("far", character["colors"]["far"])

    def limb(side: str, part: str, width_key: str, mat, to=None):
        name = skeleton["limbs"][side][part]
        end_point = head(skeleton["limbs"][side][to]) if to else tail(name)
        ob = mesh_object(f"{side}-{part}", cylinder(head(name), end_point, w[width_key] / 2), mat)
        attach(ob, arm, name)
        joint = mesh_object(f"{side}-{part}-joint", sphere(head(name), w[width_key] / 2, w[width_key] / 2, w[width_key] / 2), mat)
        attach(joint, arm, name)

    for side in ("left", "right"):
        mat = near if (side == "left") == left_near else far
        limb(side, "hip", "hip", mat)
        limb(side, "thigh", "thigh", mat)
        limb(side, "shin", "shin", mat)
        limb(side, "foot", "foot", mat)
        limb(side, "shoulder", "shoulder", mat)
        limb(side, "upperArm", "upperArm", mat)
        limb(side, "forearm", "forearm", mat)
    for name in skeleton["torso"]:
        ob = mesh_object(name, cylinder(head(name), tail(name), w["torso"] / 2), near)
        attach(ob, arm, name)
        cap = mesh_object(f"{name}-joint", sphere(head(name), w["torso"] / 2, w["torso"] / 2, w["torso"] / 2), near)
        attach(cap, arm, name)
    hb = skeleton["head"]
    centre = head(hb) + (tail(hb) - head(hb)) * 0.5
    hw, hh = character["head"]["width"] * height / 2, character["head"]["height"] * height / 2
    ob = mesh_object("head", sphere(centre, hw, hw, hh, align=tail(hb) - head(hb)), near)
    attach(ob, arm, hb)
    arm.data.pose_position = "POSE"
    arm.hide_render = True

    # Frame the window from the side, the motion running left to right.
    pts = []
    for f in range(start, end + 1, 2):
        scene.frame_set(f)
        for b in bones:
            pts.append(arm.matrix_world @ b.head)
            pts.append(arm.matrix_world @ b.tail)
    xs = [p.dot(forward) for p in pts]
    zs = [p.z for p in pts]
    pad = 0.08 * height
    span = max(max(xs) - min(xs), max(zs) - min(zs)) + 2 * pad
    cx, cz = (max(xs) + min(xs)) / 2, (max(zs) + min(zs)) / 2
    mid_depth = sum(p.dot(view) for p in pts) / len(pts)
    target = forward * cx + view * mid_depth + Vector((0, 0, cz))
    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = span
    cam_data.clip_end = 100
    cam = bpy.data.objects.new("cam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = target - view * 10
    cam.rotation_euler = view.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    # Flat, exact colour on a transparent background.
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "FLAT"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.render_aa = "16"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = a.size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    os.makedirs(a.out, exist_ok=True)
    scene.render.filepath = os.path.join(a.out, "")
    scene.frame_start, scene.frame_end = start, end

    # Where the fast foot is at its peak, in output pixels, for placing a ball.
    scene.frame_set(peak)
    toe = tail(skeleton["limbs"][kick_side]["toe"])
    p = world_to_camera_view(scene, cam, toe)
    ground = world_to_camera_view(scene, cam, Vector((toe.x, toe.y, 0)))
    meta = {
        "fps": a.fps,
        "frames": end - start + 1,
        "files": "0001.png onwards, one per frame",
        "peakFrame": peak - start,
        "movingSide": kick_side,
        "toeAtPeak": [p.x * a.size, (1 - p.y) * a.size],
        "groundY": (1 - ground.y) * a.size,
        "pixelsPerMetre": a.size / span,
        "figureHeightPx": height * a.size / span,
        "ballDiameterPx": character["ball"]["diameter"] * height * a.size / span,
        "source": os.path.basename(a.bvh),
    }
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w"), indent=2)

    # Keep the scene, so a person can open it in Blender to inspect, tweak, or learn from it.
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "scene.blend"))
    scene.render.filepath = os.path.join(a.out, "")
    bpy.ops.render.render(animation=True)
    # Blender names frames by scene frame number; renumber from 0001 for the video.
    for i, f in enumerate(range(start, end + 1), 1):
        src = os.path.join(a.out, f"{f:04d}.png")
        if os.path.exists(src):
            os.replace(src, os.path.join(a.out, f"r{i:04d}.png"))
    for i in range(1, end - start + 2):
        os.replace(os.path.join(a.out, f"r{i:04d}.png"), os.path.join(a.out, f"{i:04d}.png"))
    print("RENDERED", json.dumps(meta))


if __name__ == "__main__":
    main()
