# Characters

A character is a style file applied to a moving skeleton. The skeleton comes from recorded or
generated motion; the style decides how it looks. Proven on a recorded football kick,
2026-10-21.

## Motion

BVH is the interchange format: Blender imports it natively, and most sources export it.

| Source | Use | Licence |
| --- | --- | --- |
| [CMU motion capture](http://mocap.cs.cmu.edu/) | Sports, everyday actions; search by keyword | "May be copied, modified, or redistributed without permission" (CMU FAQ) |
| Mixamo | Stylised actions on a rigged figure; FBX | Needs the person's Adobe account; read Adobe's terms |
| Keyed by hand | Simple poses a library lacks | Ours |
| Text-to-motion models | Later | Check each model; many are trained on research-only data |

CMU ships Acclaim files (`.asf` skeleton, `.amc` motion). Convert them:

```bash
python3 scripts/acclaim_to_bvh.py 10.asf 10_01.amc 10_01.bvh
```

The conversion was checked against Blender's import to four decimal places.

## Style

A style file in `local/blender/characters/` holds colours and widths as fractions of standing
height, so one style fits any skeleton:

```json
{ "colors": { "near": "#F2EFE8", "far": "#C9C5BC" },
  "widths": { "torso": 0.118, "thigh": 0.108, "shin": 0.084, "upperArm": 0.062 },
  "head": { "width": 0.175, "height": 0.235 } }
```

`scripts/skeletons.json` maps each skeleton's bone names (CMU so far) to the parts a style
draws. A new skeleton needs one entry there, nothing else.

## Render

```bash
Blender -b --python scripts/render_character.py -- --bvh 10_01.bvh \
  --character local/blender/characters/striker.json --skeleton cmu \
  --out local/blender/renders/kick-10_01
```

- Limbs are round in section, so their drawn width never changes as they twist.
- The far side's limbs take the far colour, so overlapping legs stay readable.
- The camera is orthographic and looks across the motion, which runs left to right.
- With no `--frames`, it renders the window around the fastest foot movement (`--before`,
  `--after` in seconds) and writes that peak to `meta.json` with the toe's pixel position.

## Known limits

- Proportions are the recording's, not a stylised mark's. A logo-faithful character needs a
  style with its own proportions, a later module.
- Hands, fingers and toes are not drawn.
