# Characters

A character job has three parts that change independently, each a script in `scripts/`:

| Part | Script | Makes | Changes when |
| --- | --- | --- | --- |
| Character | `build_character.py` | `characters/<name>.blend`: one mesh bound to a skeleton | the look or build changes |
| Motion | `make_motion.py` | `motion/<clip>.blend`: actions on our skeleton | a new action is needed |
| Shot | `render_shot.py` | `renders/<shot>/`: PNG frames, `meta.json`, `scene.blend` | a video needs a clip |

A new character plays every existing motion; a new motion plays on every character. Proven on
ScoutRoom's striker kicking, 2026-10-21.

## Character

A design file, `local/blender/characters/<name>.json`, holds the whole character in metres,
standing at the origin and facing -Y. Only the left side is written; `.L` parts mirror to `.R`.

- `joints`: named points; `bones`: `[name, from, to, parent]`, parents first.
- `shapes`: body parts, each a list of blobs `[joint or point, radius or [rx, ry, rz]]`. A part
  is the smooth hull around its blobs, so a calf or a chest is one more blob.
- `colours`: `body`, `far` (the far side's limbs in a side shot), `background` (check renders).
- `checkPoses`: test poses, bone to world direction.

The build makes the skeleton, hulls every part, fuses the parts into one watertight mesh (voxel
remesh), softens the joins, binds the mesh with automatic weights, and saves the `.blend` in
seconds. `--check <folder>` renders front, side, a map of which bone moves each part, and the
test poses: judge the physique there before animating.

```bash
Blender -b --python scripts/build_character.py -- --design striker.json \
  --out striker.blend --check local/blender/renders/striker-check
```

In Blender, select `rig` and press Ctrl+Tab for Pose Mode to bend bones; select `body` and use
Weight Paint mode to see each bone's pull.

## Motion

| Source | Use | Licence |
| --- | --- | --- |
| [CMU motion capture](http://mocap.cs.cmu.edu/) | Sports and everyday actions; search by keyword | "May be copied, modified, or redistributed without permission" (CMU FAQ) |
| Keyed by hand | Poses a library lacks, as pose layers | Ours |
| Text-to-motion models | Later | Check each model; many are trained on research-only data |

CMU ships Acclaim files; convert them with `python3 scripts/acclaim_to_bvh.py 10.asf 10_01.amc
10_01.bvh` (checked against Blender's import to four decimal places).

`make_motion.py` retargets a BVH onto a character's skeleton through `scripts/bone_maps.json`
(ours to theirs; a new source skeleton needs one entry). Each of our bones copies the turn its
source bone made from rest, so the skeletons may differ in proportion and bone count. Then it
cleans up, as any retarget must:

- planted feet (low and still in the recording) rest on the floor, by moving the hips;
- a swinging foot that would cut the floor is lifted clear by two-bone IK.

Pose layers exaggerate a recording without touching it. Each moves one bone in the side view
over `times` (seconds from the fastest foot: ease in, full, hold, ease out): `aim` points it at
a screen angle (0 ahead, 90 up, 180 behind, 270 down), `degrees` turns it, clockwise positive.
Leave the planted leg and the hips alone, or the planted foot slides.

```bash
Blender -b --python scripts/make_motion.py -- --character striker.blend \
  --bvh 10_01.bvh --map cmu --layers 10_01-strike.json --out kick-10_01.blend
```

The cleanup and the layers sit in a second action, combined over the recording in the NLA
editor. The motion also records its key moment, so a layer that changes the foot's speed cannot
shift every shot's window.

## Shot

```bash
Blender -b --python scripts/render_shot.py -- --character striker.blend \
  --motion kick-10_01.blend --out local/blender/renders/strike-10_01 --before 0.4 --after 0.6
```

The shot stacks the motion in the NLA editor, films it orthographically from the side it
travels across (left to right), shades the far side, and renders flat colour on transparency.
`meta.json` gives the video `fps`, `size`, `frames`, `peakFrame`, `groundY` (where the feet rest),
`pixelsPerMetre`, `figureHeightPx`, and `toePath`, the moving toe's pixel on every frame, so a
ball can be timed to the foot. Render at 120 fps when the video slows or reverses the clip.

## Vector masters

`trace_svg.py` turns a flat still, such as a logo rendered at 3x, into an SVG: one layer per
palette colour, traced at sub-pixel accuracy. ScoutRoom's mark (21 KB) came from:

```bash
python3 scripts/trace_svg.py logo-3240.png scoutroom-mark.svg \
  --palette "#0B0E11" "#C9C5BC" "#F2EFE8" "#E8B34B" \
  --layers "#C9C5BC+#F2EFE8" "#F2EFE8" "#E8B34B" --hole "#E8B34B=#0B0E11"
```

Needs numpy. Compare the SVG, rendered back (`qlmanage -t`), against the still.

## Check

- Lay out frames around every key moment with `direct-video`'s `frame_grid.sh`.
- For floor faults, measure each frame's lowest pixel against `groundY`.
- `motion_audit.py` flags a real kick's fastest frames; a one-frame strip shows whether the
  motion is continuous.

## Known limits

- Side views only: layers and shots work in the side plane.
- Hands are mittens; feet have no toes.
- Planted feet are held to the floor but may slide a little sideways.
