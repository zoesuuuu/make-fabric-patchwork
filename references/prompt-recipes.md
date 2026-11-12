# 拼布画 Prompt 配方

本文件把 [style-system.md](style-system.md) 翻译成可复用的图像生成指令。所有提示词用英文书写，`<...>` 用实际内容替换。

## 先判断模式

| 用户说法 | 模式 | 做法 |
| --- | --- | --- |
| “把这张照片做成拼布画，加在图片角落” | A · 角落贴片 | AI 生成透明布片主体，Python 合成到照片角落 |
| “把这张照片做成拼布画 / 只要拼布画” | B · 照片转独立作品 | AI 生成完整拼布画 |
| 没有图片，只有文字描述 | C · 描述生成 | AI 生成完整拼布画 |
| “只改某处，其他不变” | D · 局部修改 | 定向重绘，保留已确认属性 |

工艺模式（A、B、C 通用）：

- 默认 **appliqué**：一个主体、6–15 块宽大布片、缝线固定。
- 用户说“碎布 / 拼布块 / 多图案” → **fabric collage**：10–24 块图案碎布。
- 用户说“几何 / 方块 / 三角” → **geometric patchwork**：16–60 个规则单元。
- 用户说“毛毡 / 儿童 / 卡通” → **felt appliqué**：5–20 块纯色毛毡、干净剪边。

## Prompt 字段与 style-system 的对应

| Prompt 字段 | 来源章节 |
| --- | --- |
| Subject / construction | 布片形状与构造 |
| Materials | 布料材质库 |
| Edges / stitches | 布片边缘、针脚与手工痕迹 |
| Composition / framing | 构图 |
| Color palette | 配色 |
| Lighting | 光影 |
| Avoid | 排除项 |

## 平面硬约束（所有模式默认追加）

```text
Flatness: strictly flat 2D appliqué sewn flush onto the cloth; no padding, stuffing, raised or lifted edges, bevels, cloth-thickness highlights, drop shadows, or 3D relief; use only a hairline seam darkening where pieces overlap.
```

## 清晰度硬约束

```text
Clarity: generate at the model's native high resolution; crisp cut edges and legible stitches; no soft focus, haze, bloom, grain, or painterly blur; when the motif will be inset at a small size, keep the silhouette simple rather than adding fine detail.
```

成品不要放大低分辨率原图。原图短边低于 800 px 时，优先要求用户导出更高分辨率版本。

## 模式 A：照片 + 拼布双区画纸

### 流程

1. 读取照片，确定主体和 1–3 个识别锚点。
2. 生成**一张透明 RGBA 布片主体**：不含底布、卡片、文字、投影。
3. Python 合成器造一张浅黄色布面画纸：上方放原照片，下方单独放拼布，两个区域不重叠。
4. 画纸四周加棕色细线和棕色缝线，照片外沿加棕色针脚；照片像素保持原样。
5. 默认不加标题；只有改用手工布卡模式时才用 Python 排版标题。

### 生成透明主体的提示词

```text
Use case: transparent motif generation for a two-zone photo-and-patchwork sheet
Asset type: one isolated text-free hand-stitched patchwork motif with genuine alpha transparency outside the motif
Primary request: Build a compact fabric-patchwork interpretation of the supplied photo's main subject.
Input images: Image 1 is a subject reference only. Preserve <anchor 1>, <anchor 2>, and <anchor 3>; do not reproduce the photo rectangle, background, text, or framing.
Scene/backdrop: genuine transparent RGBA outside the motif; no fabric base, no paper, no card, no panel, no colored matte, no checkerboard, no stamp, no caption, no page shadow.
Subject: one complete, readable <subject> built from 8–16 broad fabric pieces; retain only the anchors that make it recognizable; facial identity is not required.
Style/medium: flat, front-facing cut-fabric appliqué; the subject is made of cloth, not a drawing with a fabric texture overlay; matte cotton and linen with visible weave; printed patterns such as <pattern 1>, <pattern 2>, or gingham may replace flat color; low-saturation warm craft palette.
Construction: broad coherent planes; 1–2 flush layers; adjacent light, middle, and dark fabric pieces may suggest form but must stay perfectly flat; no padding, raised edges, bevels, or plush volume; no confetti-like fragments.
Edges: raw frayed edges on 30–70% of pieces with short irregular fibers; clean cut edges elsewhere; a visible running, blanket, or zigzag stitch fixes 40–70% of the outer contour; thread 1–3 px equivalent, slightly uneven spacing.
Composition/framing: the complete motif sits fully inside the canvas with at least 8% empty transparent margin on every side; no clipped fabric, no cropped stitch, no drop shadow; separate overlaps only with a 1–2 px hairline seam.
Lighting: even flat light; no object shadows and no volume shading.
Color palette: 2–3 chromatic colors from <palette> plus one muted accent and one cream or linen neutral; do not exceed 5 chromatic colors.
Text: none.
Constraints: the alpha channel must be truly transparent around the complete motif; the motif must read as flat sewn cloth at small size with crisp edges; keep the silhouette simple enough to survive a 20% inset.
Avoid: fabric base, paper, card, frame, caption, stamp, banner, background rectangle, opaque matte, colored halo, checkerboard preview, digital gradient, glossy vector fill, plastic or metallic sheen, photoreal fabric photo, tape, paper craft, 3D relief, padding, stuffing, raised or lifted edges, bevel, drop shadow, dense mosaic, tiny confetti scraps, perfect computer stitching, watermark, signature, pseudo-text.
```

### Python 合成约定

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| 版式 | 上下双区画纸 | 上方原图，下方拼布，不重叠 |
| 画纸背景 | 浅暖黄布面 `#F4E6C4` | 用户可指定更浅或更暖的黄色 |
| 页边框 | 棕色细线 + 棕色缝线 | 默认线色 `#7A4E35` |
| 照片位置 | 上方 | 约占画布面积 60–65%，原像素不缩放 |
| 照片针脚 | 外沿棕色针脚 | 针脚不能画进照片像素 |
| 拼布位置 | 下方 | 约占画布 20–25%，直接落在黄布面 |
| 两区间隙 | 照片短边的 3.5% | 建议 2–5%，绝不重叠 |
| 阴影 | 无 | 照片和拼布都不加投影 |
| 照片像素 | 不变 | 不重绘、不调色、不拉伸 |

合成检查：照片与拼布两个矩形完全不重叠；照片像素不变；拼布完整、无裁切；页边框和照片针脚清晰可见。

### 无脚本直出（仅回退）

当宿主既不能运行 Python、也不能做图层合成时，才把下面的请求交给图像编辑模型。它会重绘整张图，照片保真度不如合成器，因此必须逐项检查“原图未变”。

```text
Use case: compositing
Asset type: final portrait sheet with one photo zone and one patchwork zone
Primary request: Create one warm pale-yellow fabric page with two separate, non-overlapping zones: the supplied photo above and a flat patchwork interpretation below.
Input images: Image 1 is the photo to preserve. Place it unchanged in the upper zone at about 60–65% of the sheet area; do not redraw, recolor, crop, or relight it.
Page: warm light-yellow fabric background, thin brown line and brown stitching around the page edges.
Photo mounting: add a brown stitch border just outside the photo edges; never draw stitches over photo pixels.
Subject: build the lower patchwork from the photo's main subject using <1–3 anchors>; it must read as cut fabric, not a drawing with a fabric texture.
Style/medium: strictly flat 2D appliqué, matte cotton and linen, visible weave, raw fray on 30–70% of pieces, running or blanket stitch, low-saturation warm craft palette.
Composition/framing: photo above, patchwork below, with a 3–5% gap; the two zones must never overlap; patchwork occupies about 20–25% of the canvas; no card or caption.
Flatness: no padding, stuffing, lifted edges, bevels, cloth-thickness highlights, drop shadows, or 3D relief; only a hairline seam between overlapping pieces.
Lighting: keep the photo's original light; the patchwork sits flat on the page with no cast shadow.
Text: none.
Constraints: preserve the photo pixels exactly; keep the photo larger than the patchwork; keep both elements fully inside the page.
Avoid: overlapping zones, photo overlay, card, panel, second background, global color grade, global blur, 3D relief, padding, stuffing, raised edges, bevel, drop shadow, watermark, text.
```

## 模式 B：照片转独立拼布画

```text
Use case: image-to-image stylized transformation
Asset type: finished 3:4 portrait hand-stitched fabric patchwork artwork
Primary request: Transform the supplied photo into a standalone patchwork artwork made of cut and sewn cloth.
Input images: Image 1 is the subject reference. Preserve <anchor 1>, <anchor 2>, and <anchor 3>. Do not carry over its background, room, hands, furniture, or original framing.
Scene/backdrop: one continuous base cloth such as cream cotton, oatmeal linen, soft gingham, polka-dot cotton, or thin-stripe fabric; quiet and low contrast; optional 3–8% patterned binding or border; no room, wall, table, or hanging hardware.
Subject: one clear <subject>, rebuilt from broad fabric pieces; 1–3 identification anchors; facial identity is not required; simplify aggressively rather than reproducing every detail.
Style/medium: strictly flat 2D front-facing hand-stitched patchwork; <MODE> construction with <PIECE COUNT> coherent pieces; subject-as-fabric, never an illustration with a fabric texture overlay; matte cotton, linen, felt, or burlap with visible weave; printed patterns substitute for flat color.
Composition/framing: subject bounding box about 50–72% of canvas width and 45–65% of height; centered or slightly below center; at least 8% safe margin from every edge; 25–40% quiet base cloth.
Color palette: <2–4 chromatic colors + 1 accent + 1–2 neutrals>; low saturation; patterns carry color where useful; at most one strong accent.
Materials/textures: mix at least two fabrics or two printed patterns; pattern repeat about 2–8% of the piece's short side; no photorealistic floral prints.
Edges/stitches: raw frayed edges on 30–70% of pieces with short irregular fibers; clean cut edges elsewhere; visible running, blanket, or zigzag stitches along 40–80% of the main contour; 1–3 thread colors; slightly uneven spacing with occasional loose thread ends.
Flatness: pieces stay flush and pressed onto the base cloth; 1–2 layers only; no padding, stuffing, lifted corners, bevels, cloth-thickness highlights, or drop shadows; divide overlaps with a crisp 1–2 px seam line at ≤12% darkening.
Lighting/mood: soft window daylight, low contrast, warm handmade calm.
Text: none unless explicitly requested.
Constraints: the artwork must still read as sewn cloth when the texture is mentally removed; keep broad planes; keep any fragmented color patches below 30% of the subject area; the whole result must look flat and pressed, not sculptural.
Avoid: digital gradient, glossy vector fill, plastic or metallic sheen, photoreal fabric-photo collage, tape collage, paper craft, 3D plush, padding, stuffing, raised or lifted edges, bevels, drop shadows, paper-sculpture depth, dense mosaic, confetti fragments, rainbow palette, perfect computer stitching, uniform white outline, room decor, hands, tools, hanging rod, vintage grunge, stains, watermark, signature, pseudo-text.
```

### 变体替换

| 用户需求 | 替换写法 |
| --- | --- |
| 碎布拼贴 | `fabric collage construction with 10–24 patterned fabric scraps` |
| 几何拼布 | `geometric patchwork construction with 16–60 square or triangle units` |
| 毛毡 | `felt appliqué with 5–20 solid felt pieces and clean scissor-cut edges` |
| 柔和氛围 | 降低对比、增加留白、减少图案数量 |

## 模式 C：文字描述生成

```text
Use case: stylized-concept
Asset type: finished 3:4 portrait hand-stitched fabric patchwork artwork
Primary request: Create a fabric patchwork artwork about <theme>.
Scene/backdrop: one continuous quiet base cloth in cream cotton, oatmeal linen, soft gingham, or thin-stripe fabric; optional 3–8% patterned border; no room or desk context.
Subject: invent one clear motif or one compact scene that expresses <idea>; use <1–3 recognizable objects> rather than illustrating every noun; keep one dominant anchor.
Style/medium: strictly flat 2D front-facing hand-stitched patchwork; <appliqué | fabric collage | geometric patchwork | felt appliqué> construction with <piece count> coherent pieces; matte cloth with visible weave; printed patterns such as <pattern 1> and <pattern 2> replace flat color.
Composition/framing: subject occupies about 50–70% of the canvas; generous negative space of 25–40%; safely inset 8% from all edges; gentle asymmetry preferred.
Color palette: <2–4 chromatic colors + 1 accent + neutrals>; muted warm craft palette; at most one strong accent; no rainbow.
Materials/textures: mix at least two fabrics or patterns; scale prints to 2–8% of the piece's short side; keep trims such as lace or rickrack below 10% of the area.
Edges/stitches: raw fray on 30–70% of pieces; clean cuts elsewhere; running, blanket, or zigzag stitching along 40–80% of the contour; 1–3 thread colors; slight imperfection.
Flatness: 1–2 flush layers; no padding, stuffing, raised edges, bevels, or drop shadows; only a hairline seam where pieces overlap.
Lighting/mood: soft ambient daylight; mood <quiet | playful | nostalgic | warm minimal>.
Text: none unless explicitly requested.
Constraints: keep one readable motif; the cloth construction must stay legible; the result must remain flat; no dense narrative clutter.
Avoid: digital gradient, glossy vector, photoreal fabric photo, tape or paper craft, 3D plush, padding, stuffing, raised edges, bevels, drop shadows, dense mosaic, confetti fragments, rainbow palette, perfect machine stitching, room context, tools, watermark, signature, pseudo-text.
```

## 附加：标题

仅在用户要求文字时追加：

```text
Text (verbatim): "<EXACT TEXT>"
Typography: one short hand-stitched or typewriter-style caption, at most 3 English words or 8 Chinese characters, deep cocoa or charcoal thread/ink, placed on the base cloth with a safe margin; not overlapping the subject.
Constraints: reproduce the quoted characters exactly; no filler text, brand names, dates, or pseudo-writing.
```

模式 A 的标题在主体生成之后由 Python 排版，不让模型画字。

## 附加：局部修改

```text
Edit only <failed property>.
Keep unchanged: <approved subject>, <approved fabric construction>, <approved palette>, <approved composition>, <approved base cloth>, and <exact text or no-text state>.
Correct <specific defect> with <one concrete change>.
Do not add any new object, decoration, wording, logo, signature, or watermark.
```

只允许一次定向修正；构图、边距、文字、放置位置这类几何问题必须用脚本修正，不重新生成。

## 示例

### 猫照片 + 角落贴片（模式 A）

```text
Use case: transparent motif generation for a corner-inset patchwork label
Asset type: one isolated text-free patchwork motif with genuine alpha transparency
Primary request: Build a compact fabric-patchwork interpretation of the supplied cat photo.
Input images: Image 1 is a subject reference only; preserve the ear shape, tail gesture, and seated pose; do not reproduce the photo background or frame.
Subject: one complete seated cat from 9–13 broad fabric pieces; cream muzzle, warm gray tabby body, brick-red collar; facial identity not required.
Style/medium: strictly flat cut-fabric appliqué; matte cotton with visible weave; one dotted or gingham piece; low-saturation warm palette; no raised or padded areas.
Edges: raw fray on the outer silhouette; blanket stitch in warm gray along 50–60% of the contour; slightly uneven spacing.
Composition/framing: complete motif inside the canvas with 8% transparent margin; no clipping.
Text: none.
Constraints: genuinely transparent RGBA outside the cat; readable at small size.
Avoid: fabric base, card, caption, gradient, glossy vector, photoreal fur, dense mosaic, tape, watermark.
```

### 建筑照片转独立拼布（模式 B）

```text
Transform the supplied building photo into a 3:4 hand-stitched patchwork artwork. Preserve only the building's roofline and one window rhythm; omit people, cars, signage, and surrounding street clutter. Build the facade from 10–14 broad cotton and linen pieces laid perfectly flat: cream stone, dusty blue sky band, cocoa shadow planes, and one mustard accent. Use thin-stripe fabric for the awning and small gingham for window panes. Keep the building at about 60% of the canvas with 30% quiet oatmeal-linen base cloth. Raw fray only on the roofline and awning; blanket stitch along the main contour. Strictly flat, no padding, no lifted edges, no drop shadows. No text, no room context, no gradient, no photoreal texture, no tape, no watermark.
```

### 雨天咖啡描述（模式 C）

```text
Create a 3:4 patchwork artwork about a quiet rainy afternoon in a cafe. On an oatmeal-linen base cloth, build one compact motif: a coffee cup on a saucer, a small window with three raindrops, and a folded napkin. Use 9–14 pieces in dusty blue, cream, cocoa, and one muted brick accent; one thin-stripe fabric and one small floral print. Keep the motif in the lower-middle at about 55% of the canvas and leave 35% quiet cloth. Raw fray on the napkin and cup rim; running stitch along the window frame; blanket stitch around the cup. Strictly flat, pressed onto the cloth, no padding or lifted edges, no drop shadows. No text, no people, no room furniture, no gradient, no glossy vector, no tape, no watermark.
```

## 面料词汇表

| 中文 | Prompt 用语 |
| --- | --- |
| 平纹棉布 | plain-weave cotton |
| 亚麻 | linen |
| 麻布 / 粗麻 | burlap / coarse linen |
| 毛毡 | felt |
| 红白格 | red-and-white gingham |
| 波点布 | polka-dot cotton |
| 小碎花 | small floral print |
| 细条纹 | thin-stripe cotton |
| 格纹 | plaid / check |
| 毛边 | raw frayed edge |
| 毯边缝 | blanket stitch |
| 平针 | running stitch |
| 回针 | backstitch |
| 锁边 / 锯齿缝 | zigzag stitch |
| 荷叶边 | ruffled trim |
| 包边 | binding |

## 通用约束

- 一次生成；仅当主体识别或布料质感失败时允许一次定向修正。
- 风格参考图只约束材质、构图和手工感，禁止复制其中的主体。
- 提示词保持紧凑：只保留与当前需求相关的字段，但风格、边缘、排除项三类不要省略。
- 文字、边距、放置位置、比例等精确项交给 Python，不从生成模型“碰运气”。
