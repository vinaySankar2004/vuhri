"""Turn a recording into a motion our characters can play, headless in Blender.

Opens a character (its skeleton is the target), imports a BVH recording, and retargets it: each
of our bones takes the turn its mapped source bone made from rest, in world space, so the two
skeletons may differ in proportion and bone count. The hips take the recording's travel, scaled
to our leg length, then rise or sink so each planted foot rests on the floor. A second action,
meant to sit on top in the NLA editor, lifts any swinging foot clear of the floor and, with
--layers, exaggerates poses. Saves a .blend holding only the two actions; any character with the
same bone names can play them.

Usage:
  Blender -b --python make_motion.py -- --character striker.blend --bvh 10_01.bvh --map cmu
          --out kick-10_01.blend [--layers 10_01-strike.json] [--frames a-b]
"""

import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))


def args_after_dashes():
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", required=True)
    ap.add_argument("--bvh", required=True)
    ap.add_argument("--map", default="cmu")
    ap.add_argument("--out", required=True)
    ap.add_argument("--layers", help="JSON of pose layers; see shape()")
    ap.add_argument("--frames", help="keep only this stretch of the recording, a-b")
    return ap.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def world_rot(arm, name, rest=False):
    if rest:
        return (arm.matrix_world.to_3x3() @ arm.data.bones[name].matrix_local.to_3x3()).to_quaternion()
    return (arm.matrix_world @ arm.pose.bones[name].matrix).to_quaternion()


def world_head(arm, name, rest=False):
    b = arm.data.bones[name] if rest else arm.pose.bones[name]
    return arm.matrix_world @ (b.head_local if rest else b.head)


def hierarchy(rig):
    return sorted(rig.pose.bones.keys(), key=lambda n: len(rig.pose.bones[n].parent_recursive))


def key_rotation(pb, frame, previous):
    """Key a bone's rotation, kept in the same hemisphere as the last key so it never spins."""
    q = pb.rotation_quaternion.copy()
    if previous is not None and q.dot(previous) < 0:
        q.negate()
        pb.rotation_quaternion = q
    pb.keyframe_insert("rotation_quaternion", frame=frame)
    return q


def foot_surface(rig):
    """Each foot's lowest point, from points of the body that its foot bone carries."""
    W, body = rig.matrix_world, bpy.data.objects["body"]
    surface = {}
    for s in ("L", "R"):
        g = body.vertex_groups[f"foot.{s}"].index
        to_bone = rig.data.bones[f"foot.{s}"].matrix_local.inverted() @ W.inverted() @ body.matrix_world
        pts = [v.co for v in body.data.vertices if any(e.group == g and e.weight > 0.5 for e in v.groups)]
        surface[s] = [to_bone @ p for p in pts[:: max(1, len(pts) // 300)]]

    def low(side):
        m = W @ rig.pose.bones[f"foot.{side}"].matrix
        return min((m @ p).z for p in surface[side])

    return low


def contacts(scene, src, bones):
    """Frames where each recorded foot is planted: near the recording's floor and barely moving."""
    def point(name, tail=False):
        b = src.pose.bones[name]
        return src.matrix_world @ (b.tail if tail else b.head)

    feet = {s: (bones[f"foot.{s}"], src.data.bones[bones[f"foot.{s}"]].children[0].name) for s in ("L", "R")}
    lows, toes = {s: [] for s in feet}, {s: [] for s in feet}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        for s, (ankle, toe) in feet.items():
            lows[s].append(min(point(ankle).z, point(toe, True).z))
            toes[s].append(point(toe, True))
    every = sorted(z for s in lows for z in lows[s])
    floor = every[len(every) // 20]  # the feet touch down often, so a low percentile is the floor
    planted = []
    for i in range(len(lows["L"])):
        here = set()
        for s in feet:
            step = toes[s][min(i + 1, len(toes[s]) - 1)] - toes[s][max(i - 1, 0)]
            if lows[s][i] - floor < 0.05 and Vector((step.x, step.y)).length * scene.render.fps / 2 < 0.6:
                here.add(s)
        planted.append(here)
    return planted


def ground(scene, rig, planted):
    """Move the hips up or down so a planted foot rests on z = 0; between plants, ease across."""
    low = foot_surface(rig)
    frames = list(range(scene.frame_start, scene.frame_end + 1))
    shift = [None] * len(frames)
    for i, f in enumerate(frames):
        if planted[i]:
            scene.frame_set(f)
            shift[i] = -min(low(s) for s in planted[i])
    known = [i for i, v in enumerate(shift) if v is not None]
    for i in range(len(frames)):  # fill the gaps (flight, or no contact) by straight lines
        if shift[i] is None:
            before = max((k for k in known if k < i), default=None)
            after = min((k for k in known if k > i), default=None)
            if before is None or after is None:
                shift[i] = shift[after if before is None else before]
            else:
                shift[i] = shift[before] + (shift[after] - shift[before]) * (i - before) / (after - before)
    smooth = [sum(shift[max(0, i - 3) : i + 4]) / len(shift[max(0, i - 3) : i + 4]) for i in range(len(shift))]
    hips = rig.pose.bones["hips"]
    for i, f in enumerate(frames):
        scene.frame_set(f)
        m = hips.matrix.copy()
        m.translation.z += smooth[i]
        hips.matrix = m
        hips.keyframe_insert("location", frame=f)


def retarget(scene, rig, src, bones):
    # Which way each skeleton faces at rest, from its left hip to its right hip.
    def left(arm, l, r):
        v = world_head(arm, l, True) - world_head(arm, r, True)
        return Vector((v.x, v.y, 0)).normalized()

    ours = left(rig, "thigh.L", "thigh.R")
    theirs = left(src, bones["thigh.L"], bones["thigh.R"])
    face = Quaternion((0, 0, 1), math.atan2(ours.cross(theirs).z, ours.dot(theirs)))  # ours to theirs
    unface = face.inverted()

    # Scale the hips' travel by leg length: the root's height above the toes, at rest.
    def leg(arm, hips, toe):
        return world_head(arm, hips, True).z - (arm.matrix_world @ arm.data.bones[toe].tail_local).z

    scale = leg(rig, "hips", "foot.L") / leg(src, bones["hips"], src.data.bones[bones["foot.L"]].children[0].name)

    rest_src = {t: world_rot(src, s, True) for t, s in bones.items()}
    rest_ours = {t: world_rot(rig, t, True) for t in bones}
    order = [n for n in hierarchy(rig) if n in bones]
    last = {}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        for name in order:
            turn = world_rot(src, bones[name]) @ rest_src[name].inverted()
            target = (unface @ turn @ face) @ rest_ours[name]
            pb = rig.pose.bones[name]
            if name == "hips":
                p = world_head(src, bones[name])
                head = (unface @ Vector((p.x, p.y, 0))) * scale + Vector((0, 0, p.z * scale))
            else:
                head = world_head(rig, name)
            pb.matrix = rig.matrix_world.inverted() @ Matrix.Translation(head) @ target.to_matrix().to_4x4()
            bpy.context.view_layer.update()
            last[name] = key_rotation(pb, f, last.get(name))
            if name == "hips":
                pb.keyframe_insert("location", frame=f)


def bump(t, times):
    """0 before times[0], easing to 1 by times[1], held to times[2], easing back to 0 by times[3]."""
    a, b, c, d = times

    def ease(x):
        x = min(1.0, max(0.0, x))
        return x * x * (3 - 2 * x)

    if t <= b:
        return ease((t - a) / (b - a)) if b > a else float(t >= a)
    return 1 - ease((t - c) / (d - c)) if d > c else float(t <= c)


def turn_about(rig, pb, turn, pivot):
    """Turn a pose bone, and everything below it, by a world rotation about a world point."""
    m = rig.matrix_world @ pb.matrix
    pb.matrix = rig.matrix_world.inverted() @ Matrix.Translation(pivot) @ turn.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ m
    bpy.context.view_layer.update()


def reach(rig, limb, target, hint):
    """Two-bone IK: move the end of a limb (upper, lower, end bone names) to a world point, its
    root fixed, the middle joint bending in its own plane (towards `hint`, when the limb is
    straight), the end bone keeping its angle."""
    W = rig.matrix_world
    upper, lower, end = (rig.pose.bones[n] for n in limb)
    root, mid, tip = W @ upper.head, W @ lower.head, W @ end.head
    end_rot = (W @ end.matrix).to_quaternion()
    a, b = (mid - root).length, (tip - mid).length
    to = target - root
    d = min(to.length, a + b - 1e-4)
    axis = to.normalized()
    bend = (mid - root) - axis * (mid - root).dot(axis)
    if bend.length < 0.01:
        bend = hint - axis * hint.dot(axis)
    x = (a * a - b * b + d * d) / (2 * d)
    new_mid = root + axis * x + bend.normalized() * math.sqrt(max(a * a - x * x, 0.0))
    turn_about(rig, upper, (mid - root).rotation_difference(new_mid - root), root)
    mid, tip = W @ lower.head, W @ end.head
    turn_about(rig, lower, (tip - mid).rotation_difference(root + axis * d - mid), mid)
    tip = W @ end.head
    turn_about(rig, end, end_rot.rotation_difference((W @ end.matrix).to_quaternion()).inverted(), tip)


def lift_foot(rig, side, rise, forward):
    """Raise the ankle by `rise`, the hip fixed, the foot keeping its angle."""
    ankle = rig.matrix_world @ rig.pose.bones[f"foot.{side}"].head
    reach(rig, (f"thigh.{side}", f"shin.{side}", f"foot.{side}"), ankle + Vector((0, 0, rise)), forward)


def hold(rig, layer, weight):
    """Both hands on an object held ahead of a bone, such as a controller: each wrist moves
    `weight` of the way to its grip, `at` [ahead, up] metres from the bone's head in the
    body's frame, the grips `width` apart."""
    W = rig.matrix_world
    up = Vector((0, 0, 1))
    left = W @ rig.pose.bones["thigh.L"].head - W @ rig.pose.bones["thigh.R"].head
    left = Vector((left.x, left.y, 0)).normalized()
    ahead = left.cross(up)
    centre = W @ rig.pose.bones[layer["hold"]].head + ahead * layer["at"][0] + up * layer["at"][1]
    for s, sign in (("L", 1), ("R", -1)):
        wrist = W @ rig.pose.bones[f"hand.{s}"].head
        grip = centre + left * sign * layer["width"] / 2
        reach(rig, (f"upper_arm.{s}", f"forearm.{s}", f"hand.{s}"), wrist.lerp(grip, weight), -up + left * sign)


def shape(scene, rig, layers, name, facing="motion"):
    """Clean and exaggerate the motion as an animator would, as an action combined on top.

    Cleanup is automatic: a foot that would sink below the floor is lifted clear by IK. Each pose
    layer moves one bone in the side view, with a weight that eases in and out over `times`: four
    seconds from the motion's peak (its fastest foot); without `times` it holds throughout. `aim`
    points the bone at a screen angle (0 ahead along the motion, 90 up, 180 behind, 270 down),
    flat in that view's plane; `degrees` turns it instead, positive clockwise on screen. "Ahead"
    is the way the fastest foot travels, or with facing "body" the way the hips face. A `hold`
    layer puts both hands on a held object (see hold()). The action holds, per frame, the turn
    from the recorded pose to the shaped one.
    """
    def weight(layer, t):
        return bump(t, layer["times"]) if "times" in layer else 1.0

    fps = scene.render.fps
    W = rig.matrix_world
    low = foot_surface(rig)
    floor = 0.0  # planted feet were grounded here by ground()

    feet = {s: [] for s in ("L", "R")}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        for s in feet:
            feet[s].append(W @ rig.pose.bones[f"foot.{s}"].tail)
    speed, side, i = max(
        ((Vector(((p[k] - p[k - 1]).x, (p[k] - p[k - 1]).y)).length, s, k) for s, p in feet.items() for k in range(1, len(p))),
    )
    v = feet[side][min(i + 1, len(feet[side]) - 1)] - feet[side][i - 1]
    if facing == "body":  # the hips' facing, averaged: for a motion that goes nowhere
        v = Vector()
        for f in range(scene.frame_start, scene.frame_end + 1, 4):
            scene.frame_set(f)
            v += (W @ rig.pose.bones["thigh.L"].head - W @ rig.pose.bones["thigh.R"].head).cross(Vector((0, 0, 1)))
    forward = Vector((v.x, v.y, 0)).normalized()
    peak = scene.frame_start + i

    order = hierarchy(rig)
    deltas = {}
    for f in range(scene.frame_start, scene.frame_end + 1):
        scene.frame_set(f)
        t = (f - peak) / fps
        base = {n: rig.pose.bones[n].rotation_quaternion.copy() for n in order}
        for n in order:
            mine = [l for l in layers if l.get("bone") == n and weight(l, t)]
            if not mine:
                continue
            pb = rig.pose.bones[n]
            now = ((W @ pb.matrix).to_3x3() @ Vector((0, 1, 0))).normalized()
            turn = Quaternion()
            for l in mine:
                if "aim" in l:
                    r = math.radians(l["aim"])
                    full = now.rotation_difference(forward * math.cos(r) + Vector((0, 0, 1)) * math.sin(r))
                else:
                    full = Quaternion(Vector((0, 0, 1)).cross(forward), math.radians(l["degrees"]))
                turn = Quaternion().slerp(full, weight(l, t)) @ turn
            turn_about(rig, pb, turn, (W @ pb.matrix).translation.copy())
        for l in layers:
            if "hold" in l and weight(l, t):
                hold(rig, l, weight(l, t))
        for s in ("L", "R"):
            if low(s) < floor:
                lift_foot(rig, s, floor - low(s) + 0.005, forward)
        deltas[f] = {n: base[n].inverted() @ rig.pose.bones[n].rotation_quaternion for n in order}

    recorded = rig.animation_data.action
    layer = bpy.data.actions.new(name)
    rig.animation_data.action = layer
    last = {}
    for f, by_bone in deltas.items():
        for n, q in by_bone.items():
            pb = rig.pose.bones[n]
            pb.rotation_quaternion = q
            last[n] = key_rotation(pb, f, last.get(n))
    rig.animation_data.action = recorded
    return layer, peak, side


def main() -> None:
    a = args_after_dashes()
    bones = json.load(open(os.path.join(HERE, "bone_maps.json")))[a.map]["bones"]
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(a.character))
    scene = bpy.context.scene
    rig = bpy.data.objects["rig"]
    bpy.ops.import_anim.bvh(
        filepath=os.path.abspath(a.bvh), axis_forward="-Z", axis_up="Y", global_scale=1.0,
        use_fps_scale=False, update_scene_fps=True, update_scene_duration=True,
    )
    src = next(o for o in scene.objects if o.type == "ARMATURE" and o != rig)
    src.animation_data.action.name = "recording"  # frees the clip's name for ours
    if a.frames:
        scene.frame_start, scene.frame_end = (int(x) for x in a.frames.split("-"))
    stem = os.path.splitext(os.path.basename(a.bvh))[0]

    for pb in rig.pose.bones:
        pb.rotation_mode = "QUATERNION"
    rig.animation_data_create()
    rig.animation_data.action = bpy.data.actions.new(stem)
    planted = contacts(scene, src, bones)
    retarget(scene, rig, src, bones)
    ground(scene, rig, planted)
    recorded = rig.animation_data.action
    recorded["fps"] = scene.render.fps
    doc = json.load(open(a.layers)) if a.layers else {}
    layers = doc.get("layers", [])
    suffix = os.path.splitext(os.path.basename(a.layers))[0] if a.layers else "clean"
    layer, peak, side = shape(scene, rig, layers, f"{stem}+{suffix}", doc.get("facing", "motion"))
    layer["fps"] = scene.render.fps
    layer["layerOf"] = recorded.name
    # The key moment, fixed here so a layer that changes the foot's speed cannot move it.
    recorded["peak"], recorded["side"] = peak, side
    actions = {recorded, layer}
    for act in actions:
        act.use_fake_user = True
    bpy.data.libraries.write(os.path.abspath(a.out), actions, fake_user=True)
    print("MOTION", a.out, [act.name for act in actions], scene.frame_start, scene.frame_end, scene.render.fps)


if __name__ == "__main__":
    main()
