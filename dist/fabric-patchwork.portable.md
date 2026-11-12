# Fabric Patchwork

Turn a photo or text brief into a hand-stitched fabric patchwork artwork. The subject must be built from cut and sewn cloth pieces, not an illustration with a fabric texture laid on top.

## Output contract

For photo + corner overlay:

- Build one warm pale-yellow fabric sheet (`#F4E6C4` by default) with a thin brown line and brown stitching around the page edges.
- Put the supplied photo above and the patchwork below; the two zones never overlap.
- The photo is larger: about 60–65% of the canvas area. Keep its pixels, crop, lighting, and colors unchanged.
- The patchwork occupies about 20–25% of the canvas, sits directly on the yellow page, and has no card or second background.
- Add brown stitching just outside the photo edges; never draw stitches over photo pixels.
- Keep the patchwork strictly flat: no padding, stuffing, lifted edges, bevels, cloth-thickness highlights, or 3D relief.

For standalone artwork, the base cloth is cream cotton, oatmeal linen, soft gingham, polka-dot cotton, or thin-stripe fabric. Keep 25–40% quiet negative space and 8% safe margins.

## Choose a mode

- **A — Photo + corner overlay**: keep the photo, overlay a patchwork motif in a corner.
- **B — Photo to standalone patchwork**: use the photo as subject reference, output a separate artwork.
- **C — Text to patchwork**: no photo; invent one readable motif.
- **D — Targeted revision**: change one property, keep every approved property.

Default craft mode is appliqué (6–15 broad pieces). Use fabric collage (10–24 pieces) for 碎布/拼贴, geometric patchwork (16–60 cells) for 方块/三角, and felt appliqué (5–20 clean-cut pieces) for 毛毡/儿童.

## Style rules

- Palette: 2–4 chromatic colors plus one accent and 1–2 neutrals; never more than 5 chromatic colors.
- Use at least two fabrics or printed patterns; pattern repeat about 2–8% of the piece's short side.
- Matte cotton, linen, felt, or burlap with visible weave; no photoreal fabric photos.
- Raw fray on 30–70% of pieces; clean cuts elsewhere.
- Visible running, blanket, or zigzag stitching along 40–80% of the main contour; 1–3 thread colors.
- 1–2 flush layers only. Divide overlaps with a 1–2 px hairline seam at ≤12% darkening.
- Flat, front-facing, pressed onto the cloth.

Avoid: digital gradients, glossy vector fills, plastic or metallic sheen, photoreal fabric-photo collage, tape or paper craft, 3D relief, padding, stuffing, raised or lifted edges, bevels, drop shadows, dense mosaics, confetti fragments, rainbow palettes, perfect machine stitching, room context, hands, tools, watermark, signature, pseudo-text.

## Prompt A — transparent motif for corner overlay

```text
Use case: transparent motif generation for a two-zone photo-and-patchwork sheet
Asset type: one isolated text-free hand-stitched patchwork motif with genuine alpha transparency
Primary request: Build a compact fabric-patchwork interpretation of the supplied photo's main subject.
Input images: Image 1 is a subject reference only. Preserve <1–3 anchors>; do not reproduce the photo background, frame, or text.
Scene/backdrop: genuine transparent RGBA; no fabric base, card, panel, paper, colored matte, checkerboard, caption, or page shadow.
Subject: one complete <subject> from 8–16 broad fabric pieces; facial identity is not required.
Style/medium: strictly flat 2D cut-fabric appliqué; matte cotton and linen with visible weave; printed gingham, polka dot, thin stripe, or small floral may replace flat color.
Construction: broad coherent planes; 1–2 flush layers; no padding, raised edges, bevels, or plush volume.
Edges: raw fray on 30–70% of pieces; clean cuts elsewhere; running or blanket stitch along 40–70% of the contour.
Composition: complete motif inside the canvas with 8% transparent margin; no clipping; no drop shadow.
Color: 2–3 chromatic colors from <palette> plus one accent and one neutral.
Text: none.
Constraints: genuine alpha outside the motif; crisp edges; readable at small size.
Avoid: fabric base, card, frame, caption, opaque matte, checkerboard, colored halo, gradient, glossy vector, photoreal fabric photo, tape, paper craft, 3D relief, padding, drop shadow, dense mosaic, watermark, signature, pseudo-text.
```

## Prompt B — standalone from photo

```text
Transform the supplied photo into a 3:4 hand-stitched patchwork artwork. Preserve <1–3 anchors>; discard the original background, room, hands, and framing. Use <appliqué | fabric collage | geometric patchwork | felt appliqué> with <piece count> broad pieces on one quiet base cloth. Palette: <2–4 colors + accent>. Raw fray on 30–70% of pieces; stitching along 40–80% of the contour. Strictly flat, 1–2 flush layers, no padding or drop shadows. Keep 25–40% quiet cloth and 8% safe margins. No text unless requested. No gradient, glossy vector, photoreal fabric photo, tape, 3D relief, or watermark.
```

## Prompt C — from text

```text
Create a 3:4 hand-stitched patchwork artwork about <theme>. Invent one clear motif, not every noun in the brief. Use <appliqué | fabric collage | geometric patchwork | felt appliqué> with <piece count> pieces on a quiet cream or linen base cloth. Palette: <2–4 colors + accent>. Mix at least two fabrics or patterns. Raw fray on 30–70% of pieces; visible stitching along 40–80% of the contour. Strictly flat, 1–2 flush layers, no padding, no drop shadows. Keep 25–40% negative space and 8% safe margins. No text unless requested. Avoid gradients, glossy vector, photoreal fabric, tape, 3D relief, clutter, watermark.
```

## Deterministic compositor (optional)

If Python 3.10+ and Pillow are available:

```bash
python scripts/compose_corner_patch.py \
  --photo <PHOTO> \
  --motif <TRANSPARENT_RGBA_MOTIF> \
  --output <OUTPUT> \
  --placement sheet \
  --patch-fraction 0.30
```

Run `--plan` first. The script prints `LAYOUT=sheet`, `CANVAS_SIZE`, `PHOTO_BOX`, `PHOTO_SHARE`, `PATCH_BOX`, `PATCH_SHARE`, and `PHOTO_PIXEL_VALUES=unchanged`.

## No-Python fallback

If the host can composite layers, build the pale-yellow sheet with the photo above and the transparent motif below. If it can only generate one image, use this prompt:

```text
Create one portrait sheet on a warm pale-yellow fabric background with a thin brown line and brown stitching around the page. Place the supplied photo unchanged in the upper zone at about 60–65% of the sheet area; add brown stitching just outside its edges. In the lower separate zone, build a flat patchwork motif from <1–3 anchors> at about 20–25% of the sheet area. Keep a 3–5% gap; never overlap the zones. The patchwork must be strictly flat 2D appliqué with matte cotton/linen, visible weave, raw fray on 30–70% of pieces, and running or blanket stitching. Preserve photo pixels exactly; no card, panel, second background, caption, or drop shadow. No 3D relief, padding, raised edges, watermark, or text.
```

## Validation

- Subject is formed by fabric-piece edges; seams or patches are visible inside it.
- At least one visible fray or stitch fixes the cloth.
- Palette has ≤5 chromatic colors and one accent.
- 8% safe margins; 25–40% quiet space for standalone works.
- Strictly flat: 1–2 layers, no padding, lifted edges, bevels, or drop shadows.
- Mode A: photo and patchwork are separate, non-overlapping zones; photo pixels are unchanged; page frame and photo stitch are visible.
- No gradients, glossy vector, photoreal fabric photos, tape, paper craft, 3D relief, clutter, watermark, or pseudo-text.
