"""Film a character performing a motion, headless in Blender, as a flat transparent clip.

Opens a character, loads a motion's actions and stacks them in the NLA editor (the recording,
then each layer combined on top), frames the action from the side it travels across, and renders
a transparent PNG sequence in flat colour, the far side's limbs a shade darker. `meta.json`
gives the video what it needs to line things up, and `scene.blend` keeps the shot to open.

The camera starts at the side, the character moving left to right; --angle swings it round
towards the character's front (90 faces them). "Forward" is the way the fastest foot travels,
or with --facing body the way the hips face, for motions that go nowhere, such as a dance.
Away from the side, a limb crossing the body melts into it, so --lines draws contours in the
background colour instead of shading the far side (Eevee with Freestyle, slower than flat
Workbench). --props adds simple
furniture sized to the pose: `couch` under a seated character, `controller` between the hands.

Usage:
  Blender -b --python render_shot.py -- --character striker.blend --motion kick-10_01.blend
          --out renders/strike [--size 1080] [--before 0.4] [--after 0.6] [--frames a-b]
          [--angle 0] [--facing motion|body] [--step 1] [--lines] [--props couch controller]
          [--no-features]
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


def args_after_dashes():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", required=True)
    ap.add_argument("--motion", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=1080)
    ap.add_argument("--before", type=float, default=1.0, help="seconds before the fastest foot")
    ap.add_argument("--after", type=float, default=1.2, help="seconds after it")
    ap.add_argument("--frames", help="explicit frame range a-b instead of the window")
    ap.add_argument("--angle", type=float, default=0, help="degrees from the side towards the front")
    ap.add_argument("--facing", choices=["motion", "body"], default="motion")
    ap.add_argument("--step", type=int, default=1, help="render every nth frame, for a preview")
    ap.add_argument("--lines", action="store_true", help="contour lines, for angles off the side")
    ap.add_argument("--props", nargs="*", default=[], choices=["couch", "controller"])
    ap.add_argument("--background", default="#0B0E11", help="the line colour")
    ap.add_argument("--no-features", action="store_true", help="hide eyes and other features, for a mark")
    return ap.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def linear(hex_colour: str):
    c = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return (*[v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c], 1.0)


def flat(name, colour):
    m = bpy.data.materials.new(name)
    m.diffuse_color = linear(colour)
    return m


def block(name, parts, material, bevel):
    """One object of boxes, each (centre, size) in metres, in its own frame; edges rounded."""
    bm = bmesh.new()
    for centre, size in parts:
        geom = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=Vector(size), verts=geom)
        bmesh.ops.translate(bm, vec=Vector(centre), verts=geom)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.modifiers.new("round", "BEVEL").width, ob.modifiers["round"].segments = bevel, 3
    bpy.context.scene.collection.objects.link(ob)
    return ob


def body_frame(rig):
    """The hips' head and the body's right, ahead and up, level with the floor."""
    W, up = rig.matrix_world, Vector((0, 0, 1))
    right = W @ rig.pose.bones["thigh.R"].head - W @ rig.pose.bones["thigh.L"].head
    right = Vector((right.x, right.y, 0)).normalized()
    return W @ rig.pose.bones["hips"].head, right, up.cross(right), up


def placed(ob, origin, right, ahead, up):
    ob.matrix_world = Matrix.Translation(origin) @ Matrix((right, ahead, up)).transposed().to_4x4()


def couch(scene, rig, body, frame):
    """A couch whose seat meets the seated body at `frame`: seat, back and two arms."""
    scene.frame_set(frame)
    ev = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = ev.to_mesh()
    g = body.vertex_groups["hips"].index
    seat = min((body.matrix_world @ v.co).z for v in me.vertices if any(e.group == g and e.weight > 0.5 for e in v.groups))
    ev.to_mesh_clear()
    hips, right, ahead, up = body_frame(rig)
    w, back = 0.9, 0.42  # half width; how far the backrest sits behind the hips
    parts = [
        ((0, -0.05, seat / 2), (2 * w, 0.66, seat)),  # seat
        ((0, -back - 0.09, (seat + 0.5) / 2), (2 * w, 0.18, seat + 0.5)),  # back
        ((w + 0.08, -0.12, (seat + 0.2) / 2), (0.16, 0.8, seat + 0.2)),  # arms
        ((-w - 0.08, -0.12, (seat + 0.2) / 2), (0.16, 0.8, seat + 0.2)),
    ]
    ob = block("couch", parts, flat("couch", "#232A32"), 0.04)
    placed(ob, Vector((hips.x, hips.y, 0)), right, ahead, up)
    return ob


def controller(scene, rig, frames):
    """A game controller between the palms, keyed on every frame."""
    grip = (0.05, 0.08, 0.035)  # a little larger than life, so it reads at phone size
    parts = [((0, 0, 0), (0.18, 0.075, 0.038)), ((0.07, -0.035, -0.012), grip), ((-0.07, -0.035, -0.012), grip)]
    ob = block("controller", parts, flat("controller", "#12161B"), 0.014)
    ob.rotation_mode = "QUATERNION"
    W, up = rig.matrix_world, Vector((0, 0, 1))
    for f in frames:
        scene.frame_set(f)
        palm = {s: W @ ((rig.pose.bones[f"hand.{s}"].head + rig.pose.bones[f"hand.{s}"].tail) / 2) for s in ("L", "R")}
        right = (palm["R"] - palm["L"]).normalized()
        ahead = up.cross(right).normalized()
        placed(ob, (palm["L"] + palm["R"]) / 2, right, ahead, right.cross(ahead))
        ob.keyframe_insert("location", frame=f)
        ob.keyframe_insert("rotation_quaternion", frame=f)
    return ob


def contour_lines(scene, colour, size):
    """Eevee with flat emission colours and Freestyle contours: limbs read across the body."""
    scene.render.engine = "BLENDER_EEVEE"
    scene.eevee.taa_render_samples = 16
    for m in bpy.data.materials:
        c = m.diffuse_color[:]
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = c
        nt.links.new(em.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
    scene.render.use_freestyle = True
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = size / 260
    fs = scene.view_layers[0].freestyle_settings
    ls = fs.linesets[0] if fs.linesets else fs.linesets.new("lines")
    for k in ("border", "crease", "external_contour", "suggestive_contour", "ridge_valley", "material_boundary", "edge_mark"):
        setattr(ls, f"select_{k}", False)
    ls.select_silhouette = ls.select_contour = True
    ls.linestyle = ls.linestyle or bpy.data.linestyles.new("lines")
    ls.linestyle.color = linear(colour)[:3]


def stack(rig, motion_path):
    """The recording as the bottom NLA track, each layer above it, combined."""
    with bpy.data.libraries.load(os.path.abspath(motion_path)) as (src, dst):
        dst.actions = src.actions
    recorded = next(a for a in dst.actions if "layerOf" not in a)
    rig.animation_data_create()
    ad = rig.animation_data
    for act in [recorded] + [a for a in dst.actions if a.get("layerOf") == recorded.name]:
        track = ad.nla_tracks.new()
        track.name = act.name
        strip = track.strips.new(act.name, int(act.frame_range[0]), act)
        strip.blend_type = "REPLACE" if act is recorded else "COMBINE"
    ad.action = None
    return recorded


def main() -> None:
    a = args_after_dashes()
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.character))
    scene = bpy.context.scene
    rig, body = bpy.data.objects["rig"], bpy.data.objects["body"]
    recorded = stack(rig, a.motion)
    for ob in scene.objects:
        if a.no_features and ob.parent == rig and ob.parent_type == "BONE":
            ob.hide_render = True
    fps = int(recorded["fps"])
    scene.render.fps = fps
    first, last = (int(x) for x in recorded.frame_range)

    # The fastest foot: which one, when, and which way it travels.
    def toe(side):
        return rig.matrix_world @ rig.pose.bones[f"foot.{side}"].tail

    track = {"L": [], "R": []}
    for f in range(first, last + 1):
        scene.frame_set(f)
        for s in track:
            track[s].append(toe(s).copy())
    _, side, k = max(
        (Vector(((p[i] - p[i - 1]).x, (p[i] - p[i - 1]).y)).length, s, i) for s, p in track.items() for i in range(1, len(p))
    )
    if "peak" in recorded:  # the motion fixed its key moment before any layer moved the foot
        side, k = recorded["side"], int(recorded["peak"]) - first
    peak = first + k
    if a.frames:
        start, end = (int(x) for x in a.frames.split("-"))
    else:
        start, end = max(first, peak - round(a.before * fps)), min(last, peak + round(a.after * fps))
    up = Vector((0, 0, 1))
    if a.facing == "body":  # the hips' facing, averaged over the window
        forward = Vector()
        for f in range(start, end + 1, 4):
            scene.frame_set(f)
            hips = rig.matrix_world @ rig.pose.bones["thigh.L"].head - rig.matrix_world @ rig.pose.bones["thigh.R"].head
            forward += hips.cross(up)
    else:
        forward = track[side][min(k + 1, len(track[side]) - 1)] - track[side][k - 1]
    forward = Vector((forward.x, forward.y, 0)).normalized()
    # From the camera into the picture: across the motion, swung by --angle towards its front.
    turn = math.radians(a.angle)
    view = up.cross(forward) * math.cos(turn) - forward * math.sin(turn)
    right = view.cross(up)  # screen right; from the side, the way the motion runs

    # The side away from the camera takes the far colour. With contour lines there is none:
    # off the side, a far leg can cross in front, and a darker leg in front reads as passing
    # through the other.
    scene.frame_set(peak)
    left_far = (rig.matrix_world @ rig.pose.bones["thigh.L"].head - rig.matrix_world @ rig.pose.bones["thigh.R"].head).dot(view) > 0
    if not a.lines:
        body.data.materials["left" if left_far else "right"].diffuse_color = linear(body["farColour"])

    props = []
    if "couch" in a.props:
        props.append(couch(scene, rig, body, (start + end) // 2))
    if "controller" in a.props:
        props.append(controller(scene, rig, range(start, end + 1)))

    # Frame every pose in the window, and the furniture.
    pts, lows = [], []
    for ob in props:
        scene.frame_set(start)
        pts += [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    for f in range(start, end + 1, 4):
        scene.frame_set(f)
        ev = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        me = ev.to_mesh()
        frame_pts = [body.matrix_world @ me.vertices[i].co for i in range(0, len(me.vertices), 25)]
        ev.to_mesh_clear()
        pts += frame_pts
        lows.append(min(p.z for p in frame_pts))
    # The floor is where the feet rest most of the time, not the recording's own floor.
    floor = sorted(lows)[len(lows) // 2]
    xs, zs = [p.dot(right) for p in pts], [p.z for p in pts]
    span = max(max(xs) - min(xs), max(zs) - min(zs)) * 1.12
    depth = sum(p.dot(view) for p in pts) / len(pts)
    target = right * (max(xs) + min(xs)) / 2 + view * depth + Vector((0, 0, (max(zs) + min(zs)) / 2))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type, cam.data.ortho_scale, cam.data.clip_end = "ORTHO", span, 100
    scene.collection.objects.link(cam)
    cam.location = target - view * 10
    cam.rotation_euler = view.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

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
    scene.render.dither_intensity = 0  # no noise in flat colour, so frames stay small
    scene.frame_start, scene.frame_end, scene.frame_step = start, end, a.step
    if a.lines:
        contour_lines(scene, a.background, a.size)
    os.makedirs(a.out, exist_ok=True)

    def px(p):
        q = world_to_camera_view(scene, cam, p)
        return [round(q.x * a.size, 1), round((1 - q.y) * a.size, 1)]

    toe_path, head_path = [], []
    frames = range(start, end + 1, a.step)
    for f in frames:
        scene.frame_set(f)
        toe_path.append(px(toe(side)))
        head_path.append(px(rig.matrix_world @ rig.pose.bones["head"].tail))
    scene.frame_set(peak)
    height = max(v.co.z for v in body.data.vertices) - min(v.co.z for v in body.data.vertices)
    meta = {
        "fps": fps / a.step,  # the rate the rendered frames play at
        "size": a.size,
        "frames": len(frames),
        "files": "0001.png onwards, one per frame",
        "peakFrame": (peak - start) // a.step,
        "movingSide": "left" if side == "L" else "right",
        "groundY": px(Vector((0, 0, floor)))[1],
        "pixelsPerMetre": a.size / span,
        "figureHeightPx": height * a.size / span,
        "character": os.path.basename(a.character),
        "motion": os.path.basename(a.motion),
        "toePath": toe_path,
        "headPath": head_path,
    }
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w"), indent=2)

    bpy.context.preferences.filepaths.save_version = 0
    scene.render.filepath = os.path.join(os.path.abspath(a.out), "")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.abspath(a.out), "scene.blend"))
    bpy.ops.render.render(animation=True)
    # Blender names frames by scene frame; renumber from 0001 for the video.
    for i, f in enumerate(frames, 1):
        os.replace(os.path.join(a.out, f"{f:04d}.png"), os.path.join(a.out, f"r{i:04d}.png"))
    for i in range(1, len(frames) + 1):
        os.replace(os.path.join(a.out, f"r{i:04d}.png"), os.path.join(a.out, f"{i:04d}.png"))
    print("RENDERED", json.dumps({k: v for k, v in meta.items() if not k.endswith("Path")}))


if __name__ == "__main__":
    main()
