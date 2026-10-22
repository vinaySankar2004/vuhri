"""Film a character performing a motion, headless in Blender, as a flat transparent clip.

Opens a character, loads a motion's actions and stacks them in the NLA editor (the recording,
then each layer combined on top), frames the action from the side it travels across, and renders
a transparent PNG sequence in flat colour, the far side's limbs a shade darker. `meta.json`
gives the video what it needs to line things up, and `scene.blend` keeps the shot to open.

Usage:
  Blender -b --python render_shot.py -- --character striker.blend --motion kick-10_01.blend
          --out renders/strike [--size 1080] [--before 0.4] [--after 0.6] [--frames a-b]
"""

import argparse
import json
import os
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector


def args_after_dashes():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", required=True)
    ap.add_argument("--motion", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=1080)
    ap.add_argument("--before", type=float, default=1.0, help="seconds before the fastest foot")
    ap.add_argument("--after", type=float, default=1.2, help="seconds after it")
    ap.add_argument("--frames", help="explicit frame range a-b instead of the window")
    return ap.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def linear(hex_colour: str):
    c = [int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return (*[v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c], 1.0)


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
    v = track[side][min(k + 1, len(track[side]) - 1)] - track[side][k - 1]
    forward = Vector((v.x, v.y, 0)).normalized()
    view = Vector((0, 0, 1)).cross(forward)  # from the camera into the picture; motion runs left to right
    if a.frames:
        start, end = (int(x) for x in a.frames.split("-"))
    else:
        start, end = max(first, peak - round(a.before * fps)), min(last, peak + round(a.after * fps))

    # The side away from the camera takes the far colour.
    scene.frame_set(peak)
    left_far = (rig.matrix_world @ rig.pose.bones["thigh.L"].head - rig.matrix_world @ rig.pose.bones["thigh.R"].head).dot(view) > 0
    body.data.materials["left" if left_far else "right"].diffuse_color = linear(body["farColour"])

    # Frame every pose in the window.
    pts, lows = [], []
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
    xs, zs = [p.dot(forward) for p in pts], [p.z for p in pts]
    span = max(max(xs) - min(xs), max(zs) - min(zs)) * 1.12
    depth = sum(p.dot(view) for p in pts) / len(pts)
    target = forward * (max(xs) + min(xs)) / 2 + view * depth + Vector((0, 0, (max(zs) + min(zs)) / 2))
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
    scene.frame_start, scene.frame_end = start, end
    os.makedirs(a.out, exist_ok=True)

    def px(p):
        q = world_to_camera_view(scene, cam, p)
        return [round(q.x * a.size, 1), round((1 - q.y) * a.size, 1)]

    toe_path = []
    for f in range(start, end + 1):
        scene.frame_set(f)
        toe_path.append(px(toe(side)))
    scene.frame_set(peak)
    height = max(v.co.z for v in body.data.vertices) - min(v.co.z for v in body.data.vertices)
    meta = {
        "fps": fps,
        "size": a.size,
        "frames": end - start + 1,
        "files": "0001.png onwards, one per frame",
        "peakFrame": peak - start,
        "movingSide": "left" if side == "L" else "right",
        "groundY": px(Vector((0, 0, floor)))[1],
        "pixelsPerMetre": a.size / span,
        "figureHeightPx": height * a.size / span,
        "character": os.path.basename(a.character),
        "motion": os.path.basename(a.motion),
        "toePath": toe_path,
    }
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w"), indent=2)

    bpy.context.preferences.filepaths.save_version = 0
    scene.render.filepath = os.path.join(os.path.abspath(a.out), "")
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(os.path.abspath(a.out), "scene.blend"))
    bpy.ops.render.render(animation=True)
    # Blender names frames by scene frame; renumber from 0001 for the video.
    for i, f in enumerate(range(start, end + 1), 1):
        os.replace(os.path.join(a.out, f"{f:04d}.png"), os.path.join(a.out, f"r{i:04d}.png"))
    for i in range(1, end - start + 2):
        os.replace(os.path.join(a.out, f"r{i:04d}.png"), os.path.join(a.out, f"{i:04d}.png"))
    print("RENDERED", json.dumps({k: v for k, v in meta.items() if k != "toePath"}))


if __name__ == "__main__":
    main()
