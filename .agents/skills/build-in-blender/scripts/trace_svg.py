"""Trace a flat-colour image into an SVG: one filled layer per colour, edges at sub-pixel accuracy.

Every pixel is split into shares of the palette's colours (an antialiased edge is a mix), each
layer's share is contoured at one half by marching squares, and each outline is simplified
within a tolerance. Layers are drawn in order, so later ones cover earlier ones; a layer may join
colours with "+" and takes the first one's colour, so a base layer can sit under the seam between
two others. A layer's holes are transparent unless --hole names a colour for them. A light blur
first keeps outlines on the shape rather than on pixel noise; specks below --speck are dropped.

Usage:
  python3 trace_svg.py logo.png mark.svg --palette "#0B0E11" "#C9C5BC" "#F2EFE8" "#E8B34B"
      --layers "#C9C5BC+#F2EFE8" "#F2EFE8" "#E8B34B" --hole "#E8B34B=#0B0E11"
      [--size 512] [--tolerance 1.0] [--blur 1.2] [--speck 40] [--tile]
"""

import argparse
import subprocess

import numpy as np

# Marching squares: corner bits tl=8, tr=4, br=2, bl=1 -> pairs of crossed edges.
# Cases 5 and 10 are saddles, resolved by the cell centre.
CASES = {
    1: [("l", "b")], 2: [("b", "r")], 3: [("l", "r")], 4: [("t", "r")], 6: [("t", "b")],
    7: [("t", "l")], 8: [("t", "l")], 9: [("t", "b")], 11: [("t", "r")], 12: [("l", "r")],
    13: [("r", "b")], 14: [("l", "b")],
}


def rgb(hex_colour):
    return [int(hex_colour[i : i + 2], 16) for i in (1, 3, 5)]


def read(path):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", path],
        capture_output=True, text=True, check=True,
    )
    w, h = (int(v) for v in probe.stdout.strip().split(","))
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(raw.stdout, np.uint8).reshape(h, w, 3).astype(np.float32)


def shares(img, palette):
    """Each pixel's share of each palette colour, summing to one (exact for four colours)."""
    a = np.vstack([np.array([rgb(c) for c in palette], np.float32).T, np.ones(len(palette))])
    flat = np.concatenate([img.reshape(-1, 3), np.ones((img.shape[0] * img.shape[1], 1), np.float32)], axis=1)
    w = flat @ np.linalg.pinv(a).T
    return np.clip(w, 0, 1).reshape(img.shape[0], img.shape[1], len(palette))


def blur(field, sigma):
    """Separable Gaussian, so outlines follow the shape rather than pixel noise."""
    r = int(3 * sigma)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    field = np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 0, field)
    return np.apply_along_axis(lambda v: np.convolve(v, k, mode="same"), 1, field)


def area(loop):
    x, y = loop[:, 0], loop[:, 1]
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2


def contours(field):
    f = np.pad(field, 1)
    inside = f > 0.5
    code = inside[:-1, :-1] * 8 + inside[:-1, 1:] * 4 + inside[1:, 1:] * 2 + inside[1:, :-1] * 1

    def cross(a, b):
        return (0.5 - a) / (b - a)

    def point(y, x, edge):
        if edge == "t":
            return ("h", y, x), (x + cross(f[y, x], f[y, x + 1]), y)
        if edge == "b":
            return ("h", y + 1, x), (x + cross(f[y + 1, x], f[y + 1, x + 1]), y + 1)
        if edge == "l":
            return ("v", y, x), (x, y + cross(f[y, x], f[y + 1, x]))
        return ("v", y, x + 1), (x + 1, y + cross(f[y, x + 1], f[y + 1, x + 1]))

    pos, links = {}, {}
    for y, x in zip(*np.nonzero((code != 0) & (code != 15))):
        c = int(code[y, x])
        if c in (5, 10):
            centre = f[y : y + 2, x : x + 2].mean() > 0.5
            pairs = [("t", "r"), ("b", "l")] if (c == 5) != centre else [("t", "l"), ("b", "r")]
        else:
            pairs = CASES[c]
        for e1, e2 in pairs:
            k1, p1 = point(y, x, e1)
            k2, p2 = point(y, x, e2)
            pos[k1], pos[k2] = p1, p2
            links.setdefault(k1, []).append(k2)
            links.setdefault(k2, []).append(k1)
    loops, seen = [], set()
    for start in links:
        if start in seen:
            continue
        loop, prev, cur = [], None, start
        while cur not in seen:
            seen.add(cur)
            loop.append(pos[cur])
            nxt = [k for k in links[cur] if k != prev]
            prev, cur = cur, nxt[0] if nxt else start
        if len(loop) > 2:
            # Back to image coordinates: undo the padding; samples sit at pixel centres.
            loops.append(np.array(loop) - 1 + 0.5)
    return loops


def simplify(points, tolerance):
    """Douglas-Peucker on a closed outline, split at its two farthest-apart points."""
    far = int(np.argmax(np.linalg.norm(points - points[0], axis=1)))

    def rdp(p):
        keep = np.zeros(len(p), bool)
        keep[0] = keep[-1] = True
        stack = [(0, len(p) - 1)]
        while stack:
            i, j = stack.pop()
            if j <= i + 1:
                continue
            a, b = p[i], p[j]
            d = b - a
            n = np.hypot(*d) or 1.0
            dist = np.abs(d[0] * (p[i + 1 : j, 1] - a[1]) - d[1] * (p[i + 1 : j, 0] - a[0])) / n
            k = int(np.argmax(dist))
            if dist[k] > tolerance:
                keep[i + 1 + k] = True
                stack += [(i, i + 1 + k), (i + 1 + k, j)]
        return p[keep]

    first = rdp(points[: far + 1])
    second = rdp(np.vstack([points[far:], points[:1]]))
    return np.vstack([first[:-1], second[:-1]])


def contains(loop, pt):
    x, y = pt
    xs, ys = loop[:, 0], loop[:, 1]
    xs2, ys2 = np.roll(xs, -1), np.roll(ys, -1)
    hit = ((ys > y) != (ys2 > y)) & (x < (xs2 - xs) * (y - ys) / (ys2 - ys + 1e-12) + xs)
    return bool(np.count_nonzero(hit) % 2)


def path(loops, scale):
    return " ".join("M" + " L".join(f"{x * scale:.2f} {y * scale:.2f}" for x, y in loop) + "Z" for loop in loops)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("out")
    ap.add_argument("--palette", nargs="+", required=True)
    ap.add_argument("--layers", nargs="+", required=True)
    ap.add_argument("--hole", action="append", default=[], help="LAYER=COLOUR: fill this layer's holes")
    ap.add_argument("--size", type=float, default=512)
    ap.add_argument("--tolerance", type=float, default=1.0, help="pixels of the source image")
    ap.add_argument("--blur", type=float, default=1.2, help="pixels; smooths noise before tracing")
    ap.add_argument("--speck", type=float, default=40, help="square pixels; smaller loops are dropped")
    ap.add_argument("--tile", action="store_true", help="fill the background with the first palette colour")
    a = ap.parse_args()

    img = read(a.image)
    share = shares(img, a.palette)
    holes = dict(h.split("=") for h in a.hole)
    scale = a.size / max(img.shape[:2])
    w, h = img.shape[1] * scale, img.shape[0] * scale
    body = [f'<rect width="{w:.0f}" height="{h:.0f}" fill="{a.palette[0]}"/>'] if a.tile else []
    for layer in a.layers:
        field = blur(sum(share[:, :, a.palette.index(c)] for c in layer.split("+")), a.blur)
        loops = [simplify(l, a.tolerance) for l in contours(field) if area(l) > a.speck]
        loops = [l for l in loops if len(l) > 2]
        fill = layer.split("+")[0]
        body.append(f'<path fill="{fill}" fill-rule="evenodd" d="{path(loops, scale)}"/>')
        if layer in holes:
            inner = [l for l in loops if sum(contains(o, l[0]) for o in loops if o is not l) % 2]
            body.append(f'<path fill="{holes[layer]}" d="{path(inner, scale)}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}">\n' + "\n".join(body) + "\n</svg>\n"
    open(a.out, "w").write(svg)
    print("TRACED", a.out, f"{len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
