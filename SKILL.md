---
name: make-fabric-patchwork
description: Turn a supplied photo or text description into a warm hand-stitched fabric patchwork artwork, or build a pale-yellow sheet with the unchanged photo above and a patchwork below. Use for requests mentioning fabric patchwork, appliqué, fabric collage, geometric patchwork, felt appliqué, 拼布画, 布片拼贴, 贴布, 毛毡贴布, 几何拼布, 照片拼布画纸, or 照片加拼布.
---

# Make Fabric Patchwork

Create one bitmap artwork in which the subject is physically built from cut and sewn cloth. The defining move is **subject-as-fabric**: the silhouette and inner structure come from fabric pieces, not from an illustration with a cloth texture laid on top.

Apply the three-question gate before delivery:

1. With the fabric texture mentally removed, is the subject still formed by fabric-piece edges?
2. Can you see seams, overlaps, or patchwork cells inside the subject?
3. Do the edges show fibers, stitching, or a visible fixing method?

If any answer is no, rebuild the subject construction. Do not fix it by adding more texture.

## Output contract

- **Mode A final image:** one pale-yellow fabric sheet with two separate zones. The original photo sits above and the patchwork sits below; they never overlap.
- The page background is warm light yellow (`#F4E6C4` by default) with a brown edge line and a brown stitch line around the page.
- The photo is the larger element: about 60–65% of the canvas area by default. The patchwork occupies roughly 20–25%.
- Keep every photo pixel unchanged; add a brown stitch border just outside the photo edges.
- The patchwork has no card or separate background; it sits directly on the pale-yellow page and stays strictly flat.
- A direct overlay (`--placement direct`) and a fabric card (`--placement card`) remain optional alternatives, but the sheet layout is the default.

## Load the style rules

- Read [references/style-system.md](references/style-system.md) before generating.
- Read [references/prompt-recipes.md](references/prompt-recipes.md) when composing or revising a prompt.

Use `assets/style-references/` only as style evidence. Primary references are `13-strawberry-patch-applique.png` (fabric collage and raw edges), `01-sewing-machine-placemat.png` (appliqué and blanket stitch), `10-apple-patch-applique.png` (frayed square and zigzag), `12-supper-art-quilt.png` (composition and negative space), and `02-sewing-time-wall-hanging.png` (narrative layout). Never copy their subjects or text. `08-dollhouse-digital-control.png` is a negative control for digital imitation of cloth, not a material reference. `14-clothesline-soft-hanging.png` is outside the v1 flat style; do not use it as a reference.

## Interpret the request

Classify the request into one mode:

- **A · Photo + corner patchwork** — the user asks to keep the photo and add a patchwork element in a corner.
- **B · Photo to standalone patchwork** — the user supplies a photo and wants a patchwork artwork as the output.
- **C · Description generation** — no photo; build one motif from the text.
- **D · Targeted revision** — the user asks to change one property of an already approved result.

Routing defaults:

- Any mention of 保留原图, 加在角落, 贴在照片上, or a literal corner placement → Mode A.
- A supplied photo without those phrases → Mode B.
- No image input → Mode C.
- "只改…其余不变" or a specific fix on an approved image → Mode D.

User instructions override every default in this file.

## Mode A: photo + patchwork sheet

The default output is one pale-yellow fabric sheet with two separate, non-overlapping zones: the original photo above, the patchwork below. Never pass the photo into a generative full-composite edit; generate **one isolated, text-free, transparent RGBA patchwork motif**, then place it on the sheet with the compositor.

1. Inspect the photo and identify the main subject plus 1–3 recognition anchors.
2. Build the sheet: warm light-yellow fabric page, a brown line plus stitch border around the page, and the photo placed above at native pixels.
3. Generate the transparent motif with the Mode A recipe in `prompt-recipes.md`: 8–16 broad pieces, visible weave, frayed edges on 30–70% of pieces, stitching along 40–70% of the contour, strictly flat, no padding or lifted edges, no base cloth, no card, no text, no cast shadow.
4. Place the motif in the lower patch zone; add a brown stitch border just outside the photo. The two boxes must never intersect.
5. Verify that the photo pixels are unchanged, the page frame is visible, and both elements sit fully inside the canvas.

Compositor defaults:

| Parameter | Default | Range |
| --- | --- | --- |
| Placement | sheet: photo above, patchwork below | sheet, direct overlay, or card |
| Photo share | about 62% of canvas area | 58–68% |
| Patch zone | 30% of photo short side in height | 20–45% |
| Page margin | 5% of photo short side | 4–7% |
| Gap between zones | 3.5% of photo short side | 2–5% |
| Page background | warm light yellow `#F4E6C4` | user-specified warm pale color |
| Page border | brown line + brown stitch | `#7A4E35` by default |
| Photo border | brown stitch just outside the photo | no stitch on photo pixels |
| Shadow | none | no drop shadows |
| Photo pixels | unchanged | never redrawn, recolored, or stretched |

The photo and patchwork are separate objects on the same page, not a photo overlay. Keep the photo larger; do not let the patchwork touch or cover it.

## Modes B and C: standalone patchwork

Produce one finished artwork: a quiet base cloth plus one readable patchwork motif. The base cloth is one of cream cotton, oatmeal linen, soft gingham, polka-dot cotton, or thin-stripe fabric. Optionally add a 3–8% patterned border, but no room, wall, table, hands, tools, or hanging hardware.

- B: extract the subject from the photo, preserve 1–3 anchors, discard the original background and framing. Facial identity is not required.
- C: invent one clear motif; do not illustrate every noun in the brief.
- Default craft mode is appliqué (6–15 broad pieces). Use fabric collage (10–24 pieces) for 碎布/拼贴 requests, geometric patchwork (16–60 cells) for 方块/三角 等 requests, and felt appliqué (5–20 pieces, clean cut edges) for 毛毡/儿童 requests.
- At most two craft modes may be combined in one artwork.

## Set the format

- Mode A creates a new sheet around the photo; the photo itself is not resampled or stretched.
- Modes B and C default to `3:4` portrait; accept `1:1` or `4:5` when requested.
- Subject bounding box: 50–72% of width and 45–65% of height.
- Keep every motif, stitch, and text element at least 8% of the short side from the edge.
- Keep 25–40% quiet base cloth in single-subject works and at least 30% in narrative spreads.
- Palette: 2–4 chromatic colors plus one accent and 1–2 neutrals; never more than 5 chromatic colors.
- Layering: 1–2 flush layers only; no padding, stuffing, lifted edges, bevels, drop shadows, or 3D relief. Separate overlaps with a hairline seam at ≤12% darkening.
- Fragmented color patches no more than 30% of the subject area.

## Resolution and sharpness

- Never upscale the source photo; preserve its pixel dimensions.
- If the photo's short side is below 800 px, warn the user and prefer a higher-resolution export. Do not present an upscaled preview as the final artwork.
- Generate motifs at native resolution with crisp edges. When fitting a motif down, use Lanczos resampling and a mild unsharp pass; never apply global blur, haze, bloom, or grain.
- Save the final composite as PNG. Downscale only once, at the very end.

## Handle text

- Default to no text in all modes.
- When requested, allow one short caption: at most 3 English words or 8 Chinese characters, no wider than 20% of the canvas.
- Reproduce the requested characters exactly; use deep cocoa or charcoal thread/ink and hand-stitched or typewriter styling.
- In Mode A, direct overlay is text-free by default; add a caption only in the optional card mode.
- Never add filler words, brand names, dates, stamps, or pseudo-text.

## Generate or edit

Use the available image generation tool. For any photo-based request:

1. Inspect every local input image first.
2. Label each image role as subject reference, style reference, or supporting input.
3. Use local referenced-image paths when all targets are local; otherwise include the smallest set of recent conversation images that covers every target.
4. Never provide both local paths and recent-conversation image inclusion in the same call.
5. Include at most two style references when useful, and state that their subjects must not appear.

Generate once by default. Allow at most one targeted generative revision, and only when subject recognition or cloth material fails. Layout, margins, placement, caption, and aspect ratio must be corrected with Python, never by another generation.

For Mode A, use exactly one motif-generation call before compositing. Keep every approved property stable during a revision.

### Generation paths

- **Host generator (preferred):** use whatever image generation or image-editing tool the host provides. In Codex this is the built-in image tool, usually invoked with `$imagegen`; other hosts may expose a different image model, MCP tool, or no generator at all.
- **No generator available:** do not substitute a drawn placeholder or claim a result exists. Ask the user for a transparent RGBA motif, or ask them to run the prompt in a host that has an image generator; then resume at the compositor step.
- **CLI/API fallback:** only when the user explicitly chooses it. It requires an API key and API billing; use the host's documented CLI or the imagegen skill's bundled script.

The compositor accepts any suitable transparent RGBA PNG, regardless of which tool produced it.

### Portability

This skill uses the Agent Skills layout (`SKILL.md` + `references/` + `assets/` + `scripts/`), so hosts that support that layout need no rewriting.

- Codex: copy the folder to `$CODEX_HOME/skills/make-fabric-patchwork/` (or `~/.codex/skills/`).
- Claude Code / Agent Skills: copy the same folder to `~/.claude/skills/make-fabric-patchwork/`.
- Trae, WorkBuddy, or any host that only accepts a single instruction file: paste `dist/fabric-patchwork.portable.md` into its custom instructions or rules.
- Any host: the image generator is replaceable; any transparent RGBA motif works. Python is needed only for deterministic compositing.

## Compose and verify

For Mode A, run:

```bash
python scripts/compose_corner_patch.py --photo <PHOTO> --plan

python scripts/compose_corner_patch.py \
  --photo <PHOTO> \
  --motif <TRANSPARENT_RGBA_MOTIF> \
  --output <OUTPUT> \
  --placement sheet \
  --patch-fraction 0.30
```

Run `--plan` first to preview `CANVAS_SIZE`, `PHOTO_BOX`, `PHOTO_SHARE`, `PATCH_BOX`, and `PATCH_SHARE`. Use `--placement direct` or `--placement card` only when the user explicitly asks for those alternatives; captions require a card.

The compositor requires Python 3.10+ and Pillow; it has no other dependencies.

If the host cannot run Python, build the same two-zone sheet with the host's native image layers. If it also cannot composite, use the single-pass fallback prompt at the end of `references/prompt-recipes.md`; reject any result that redraws or alters the photo.

The script should print a machine-readable plan including `LAYOUT=sheet`, `CANVAS_SIZE`, `PHOTO_BOX`, `PHOTO_SHARE`, `PATCH_BOX`, `PATCH_SHARE`, `SHEET_COLOR`, `LINE_COLOR`, `PHOTO_STITCH_COLOR`, `MOTIF_FIT`, `PHOTO_PIXEL_VALUES=unchanged`, and `MOTIF_MODE=transparent-rgba`. Verify those values before delivery. Reject an opaque matte, a baked checkerboard, a colored halo, a clipped motif, or overlapping photo and patch boxes.

## Validate and refine

Inspect the result and confirm:

- The subject meets all three questions of the fabric gate.
- The artwork is strictly flat and pressed to the cloth: no padding, stuffing, lifted edges, bevels, drop shadows, or sculptural volume.
- At least two fabrics or printed patterns appear.
- At least one visible fray or stitch fixes the cloth.
- Chromatic colors stay at 5 or fewer; the accent count is 1.
- Safe margins, subject ratio, and negative-space ratio match the format rules.
- Fragment area stays below 30%; layering stays at 1–2 flush layers.
- No gradient, glossy vector, plastic sheen, photoreal fabric-photo collage, tape or paper craft, dense mosaic, or perfect computer stitching appears.
- No room, hands, tools, hanging rod, stains, grunge, watermark, or pseudo-text appears.
- Mode A keeps the photo pixels unchanged and places photo and patchwork in two non-overlapping zones.
- The page is warm light yellow with a brown edge line and stitch; the photo has a visible brown stitch border.
- Any text is exact, short, and legible.

If subject or cloth material fails, make one targeted revision using the Mode D recipe and re-check. If geometry, margins, placement, or typography fail, fix them in the compositor.

## Return

Return the final image inline. For workspace-bound work, save the file into the requested location and report the output path, the mode used, and the final prompt. For Mode A, also report the canvas size, photo share, patch zone, and page colors printed by the compositor.
