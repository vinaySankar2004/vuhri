"""Convert an Acclaim skeleton and motion (ASF + AMC, the CMU motion-capture format) to BVH.

BVH is the interchange format Blender imports natively, so every motion source ends up the
same way inside Blender. The BVH rest pose is the ASF rest pose with every joint frame aligned
to the world axes, so offsets are plain world vectors and each frame's local rotation is the
parent's world rotation undone, then the bone's world rotation applied.

Usage: python3 acclaim_to_bvh.py skeleton.asf motion.amc out.bvh [--fps 120]
Needs numpy. Lengths are converted to metres with CMU's convention (length unit, inches).
"""

import argparse
import math
import re

import numpy as np


def euler_sxyz(ax: float, ay: float, az: float) -> np.ndarray:
    """Rotation about static X, then Y, then Z, in degrees (ASF and AMC's convention)."""
    x, y, z = (math.radians(a) for a in (ax, ay, az))
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    return rz @ ry @ rx


def zxy_angles(r: np.ndarray) -> tuple:
    """Angles for BVH channels 'Zrotation Xrotation Yrotation', so r = Rz Rx Ry."""
    x = math.asin(max(-1.0, min(1.0, r[2, 1])))
    y = math.atan2(-r[2, 0], r[2, 2])
    z = math.atan2(-r[0, 1], r[1, 1])
    return tuple(math.degrees(a) for a in (z, x, y))


def parse_asf(path: str):
    text = open(path, encoding="latin-1").read()
    unit = float(re.search(r"length\s+([\d.]+)", text).group(1))
    scale = (1.0 / unit) * 0.0254  # CMU: lengths are inches times the unit
    bones = {"root": {"dir": np.zeros(3), "len": 0.0, "C": np.eye(3), "dof": ["rx", "ry", "rz"]}}
    for block in re.findall(r"begin(.*?)end", text.split(":bonedata")[1].split(":hierarchy")[0], re.S):
        name = re.search(r"name\s+(\S+)", block).group(1)
        direction = np.array([float(v) for v in re.search(r"direction\s+(\S+)\s+(\S+)\s+(\S+)", block).groups()])
        length = float(re.search(r"length\s+(\S+)", block).group(1)) * scale
        axis = [float(v) for v in re.search(r"axis\s+(\S+)\s+(\S+)\s+(\S+)", block).groups()]
        dof = re.search(r"dof\s+([^\n]+)", block)
        bones[name] = {
            "dir": direction / np.linalg.norm(direction),
            "len": length,
            "C": euler_sxyz(*axis),
            "dof": dof.group(1).split() if dof else [],
        }
    parents, children = {}, {n: [] for n in bones}
    hierarchy = text.split(":hierarchy")[1]
    for line in hierarchy.splitlines():
        parts = line.split()
        if len(parts) < 2 or parts[0] in ("begin", "end"):
            continue
        for child in parts[1:]:
            parents[child] = parts[0]
            children[parts[0]].append(child)
    return bones, parents, children, scale


def parse_amc(path: str, bones: dict, scale: float):
    frames, current = [], None
    for line in open(path, encoding="latin-1"):
        line = line.strip()
        if not line or line.startswith(("#", ":")):
            continue
        if line.isdigit():
            current = {}
            frames.append(current)
            continue
        name, *values = line.split()
        current[name] = [float(v) for v in values]
    return frames


def world_transforms(frame: dict, bones: dict, parents: dict, children: dict, scale: float):
    """Each bone's world rotation and world start position for one frame."""
    rot, start, end = {}, {}, {}
    root = frame["root"]
    rot["root"] = euler_sxyz(*root[3:6])
    start["root"] = end["root"] = np.array(root[:3]) * scale

    def visit(name: str):
        for child in children.get(name, []):
            b = bones[child]
            angles = [0.0, 0.0, 0.0]
            for value, dof in zip(frame.get(child, []), b["dof"]):
                angles["xyz".index(dof[1])] = value
            local = b["C"] @ euler_sxyz(*angles) @ b["C"].T
            rot[child] = rot[name] @ local
            start[child] = end[name]
            end[child] = start[child] + b["len"] * (rot[child] @ b["dir"])
            visit(child)

    visit("root")
    return rot, start, end


def write_bvh(out: str, bones, parents, children, frames, scale, fps: float):
    lines = ["HIERARCHY"]

    def joint(name: str, depth: int, offset: np.ndarray):
        pad = "  " * depth
        if name == "root":
            lines.append("ROOT root")
        else:
            lines.append(f"{pad}JOINT {name}")
        lines.append(pad + "{")
        lines.append(f"{pad}  OFFSET {offset[0]:.6f} {offset[1]:.6f} {offset[2]:.6f}")
        if name == "root":
            lines.append(f"{pad}  CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation")
        else:
            lines.append(f"{pad}  CHANNELS 3 Zrotation Xrotation Yrotation")
        tip = bones[name]["len"] * bones[name]["dir"]
        if children.get(name):
            for child in children[name]:
                joint(child, depth + 1, tip if name != "root" else np.zeros(3))
        else:
            lines.append(f"{pad}  End Site")
            lines.append(pad + "  {")
            lines.append(f"{pad}    OFFSET {tip[0]:.6f} {tip[1]:.6f} {tip[2]:.6f}")
            lines.append(pad + "  }")
        lines.append(pad + "}")

    joint("root", 0, np.zeros(3))
    order = []

    def walk(name: str):
        order.append(name)
        for child in children.get(name, []):
            walk(child)

    walk("root")
    lines += ["MOTION", f"Frames: {len(frames)}", f"Frame Time: {1.0 / fps:.6f}"]
    for frame in frames:
        rot, start, _ = world_transforms(frame, bones, parents, children, scale)
        values = list(start["root"])
        for name in order:
            local = rot[name] if name == "root" else rot[parents[name]].T @ rot[name]
            values += zxy_angles(local)
        lines.append(" ".join(f"{v:.5f}" for v in values))
    open(out, "w").write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("asf")
    ap.add_argument("amc")
    ap.add_argument("out")
    ap.add_argument("--fps", type=float, default=120)
    args = ap.parse_args()
    bones, parents, children, scale = parse_asf(args.asf)
    frames = parse_amc(args.amc, bones, scale)
    write_bvh(args.out, bones, parents, children, frames, scale, args.fps)
    print(f"{args.out}: {len(frames)} frames at {args.fps:g} fps, {len(bones)} joints")


if __name__ == "__main__":
    main()
