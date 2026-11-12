#!/usr/bin/env python3
"""Overlay a transparent patchwork motif directly on a photo corner.

An optional fabric card is available, but direct overlay is the default. Only
Pillow is required. The photo pixels outside the motif and its shadow are
verified to be byte-identical to the source before the output is written.
"""

from __future__ import annotations

import argparse
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageColor, ImageDraw, ImageFilter, ImageFont

CORNERS = ("tl", "tr", "bl", "br")
CARD_STYLES = ("linen", "solid", "none")

DEFAULT_CARD_COLOR = "#E9DFC9"
DEFAULT_STITCH_COLOR = "#6E4A3C"
DEFAULT_CAPTION_COLOR = "#3A302B"

CJK_FONTS = (
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/Supplemental/Songti.ttc",
)
LATIN_FONTS = (
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
)


def fraction(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a number between 0 and 1") from exc
    if not 0.0 < number < 1.0:
        raise argparse.ArgumentTypeError("must be a number between 0 and 1")
    return number


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Overlay a transparent patchwork motif directly into a photo corner.",
    )
    parser.add_argument("--photo", type=Path, required=True)
    parser.add_argument("--motif", type=Path, help="transparent RGBA patchwork motif")
    parser.add_argument("--output", type=Path, help="defaults to <photo>-patchwork.png")
    parser.add_argument("--corner", choices=CORNERS, default="br")
    parser.add_argument(
        "--placement",
        choices=("sheet", "direct", "card"),
        default="sheet",
        help="sheet: photo above + patchwork below on a pale-yellow fabric page; "
        "direct: overlay on the photo; card: optional fabric label",
    )
    parser.add_argument("--motif-size-fraction", type=fraction, default=0.30)
    parser.add_argument("--patch-fraction", type=fraction, default=0.30)
    parser.add_argument("--sheet-color", default="#F4E6C4")
    parser.add_argument("--line-color", default="#7A4E35")
    parser.add_argument("--photo-stitch-color")
    parser.add_argument("--photo-stitch-width", type=int, default=0)
    parser.add_argument("--card-fraction", type=fraction, default=0.20)
    parser.add_argument("--margin-fraction", type=fraction, default=0.04)
    parser.add_argument("--motif-fraction", type=fraction, default=0.78)
    parser.add_argument("--card-style", choices=CARD_STYLES, default="linen")
    parser.add_argument("--card-color", default=DEFAULT_CARD_COLOR)
    parser.add_argument("--stitch-color", default=DEFAULT_STITCH_COLOR)
    parser.add_argument("--stitch-width", type=int, default=0)
    parser.add_argument("--texture-strength", type=float, default=1.0)
    parser.add_argument("--shadow", choices=("none", "hairline", "soft"), default="none")
    parser.add_argument("--motif-sharpen", type=float, default=0.8)
    parser.add_argument("--caption")
    parser.add_argument("--caption-color", default=DEFAULT_CAPTION_COLOR)
    parser.add_argument("--caption-size", type=int, default=0)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--seed", type=int, default=20261112)
    parser.add_argument("--plan", action="store_true", help="print layout and exit")
    return parser.parse_args()


@dataclass(frozen=True)
class Layout:
    photo_size: tuple[int, int]
    corner: str
    margin: int
    placement: str
    box_size: int
    box: tuple[int, int, int, int]


@dataclass(frozen=True)
class SheetLayout:
    photo_size: tuple[int, int]
    canvas_size: tuple[int, int]
    margin: int
    gap: int
    photo_box: tuple[int, int, int, int]
    patch_box: tuple[int, int, int, int]


def validate(args: argparse.Namespace) -> None:
    if args.card_style == "none":
        args.placement = "direct"
    if args.placement == "card" and args.card_style == "none":
        raise SystemExit("--placement card requires --card-style linen or solid")
    if not args.photo.is_file():
        raise SystemExit(f"photo not found: {args.photo}")
    if not args.plan and args.motif is None:
        raise SystemExit("--motif is required unless --plan is used")
    if args.motif is not None and not args.motif.is_file():
        raise SystemExit(f"motif not found: {args.motif}")
    if not 0.10 <= args.card_fraction <= 0.35:
        raise SystemExit("--card-fraction must be between 0.10 and 0.35")
    if not 0.20 <= args.motif_size_fraction <= 0.40:
        raise SystemExit("--motif-size-fraction must be between 0.20 and 0.40")
    if not 0.20 <= args.patch_fraction <= 0.45:
        raise SystemExit("--patch-fraction must be between 0.20 and 0.45")
    if not 0.01 <= args.margin_fraction <= 0.08:
        raise SystemExit("--margin-fraction must be between 0.01 and 0.08")
    if not 0.60 <= args.motif_fraction <= 0.90:
        raise SystemExit("--motif-fraction must be between 0.60 and 0.90")
    if args.texture_strength < 0:
        raise SystemExit("--texture-strength must be zero or positive")
    if not 0.0 <= args.motif_sharpen <= 2.0:
        raise SystemExit("--motif-sharpen must be between 0.0 and 2.0")
    if args.caption and args.placement != "card":
        raise SystemExit("--caption requires --placement card")
    for name in ("sheet_color", "line_color"):
        try:
            ImageColor.getrgb(getattr(args, name))
        except ValueError as exc:
            raise SystemExit(f"--{name.replace('_', '-')} must be a color") from exc
    if args.photo_stitch_color is not None:
        try:
            ImageColor.getrgb(args.photo_stitch_color)
        except ValueError as exc:
            raise SystemExit("--photo-stitch-color must be a color") from exc


def resolve_layout(
    photo_size: tuple[int, int],
    corner: str,
    placement: str,
    box_fraction: float,
    margin_fraction: float,
) -> Layout:
    width, height = photo_size
    short = min(width, height)
    margin = max(2, round(margin_fraction * short))
    card = round(box_fraction * short)
    card = min(card, short - 2 * margin - 1)
    if card < 32:
        raise SystemExit("photo is too small for the requested card size")
    if corner == "tl":
        x0, y0 = margin, margin
    elif corner == "tr":
        x0, y0 = width - margin - card, margin
    elif corner == "bl":
        x0, y0 = margin, height - margin - card
    else:
        x0, y0 = width - margin - card, height - margin - card
    return Layout(
        photo_size=photo_size,
        corner=corner,
        margin=margin,
        placement=placement,
        box_size=card,
        box=(x0, y0, x0 + card, y0 + card),
    )


def resolve_sheet_layout(
    photo_size: tuple[int, int],
    patch_fraction: float,
) -> SheetLayout:
    width, height = photo_size
    short = min(width, height)
    margin = max(8, round(0.05 * short))
    gap = max(6, round(0.035 * short))
    patch_height = max(round(patch_fraction * short), 120)
    patch_height = min(patch_height, round(0.45 * short))
    canvas_width = width + 2 * margin
    canvas_height = height + 2 * margin + gap + patch_height
    photo_box = (margin, margin, margin + width, margin + height)
    patch_box = (
        margin,
        margin + height + gap,
        margin + width,
        margin + height + gap + patch_height,
    )
    return SheetLayout(
        photo_size=photo_size,
        canvas_size=(canvas_width, canvas_height),
        margin=margin,
        gap=gap,
        photo_box=photo_box,
        patch_box=patch_box,
    )


def load_motif(path: Path) -> Image.Image:
    image = Image.open(path)
    if image.mode not in ("RGBA", "LA", "PA"):
        raise SystemExit(
            f"motif must have transparency (got mode {image.mode}); "
            "reject opaque mattes and checkerboard previews"
        )
    motif = image.convert("RGBA")
    alpha = motif.getchannel("A")
    low, high = alpha.getextrema()
    if high == 0:
        raise SystemExit("motif is fully transparent")
    if low == 255:
        raise SystemExit(
            "motif has no transparent pixels; regenerate it on a transparent RGBA canvas"
        )
    bbox = alpha.getbbox()
    if bbox is None:
        raise SystemExit("motif has no visible pixels")
    motif = motif.crop(bbox)
    # Small transparent pad keeps blur and resampling from clipping edge fibers.
    padded = Image.new("RGBA", (motif.width + 4, motif.height + 4), (0, 0, 0, 0))
    padded.alpha_composite(motif, (2, 2))
    return padded


def rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return mask


def soft_noise_field(
    size: int,
    cells: int,
    low: int,
    high: int,
    blur: float,
    seed: random.Random,
) -> Image.Image:
    cells = max(2, cells)
    small = Image.new("L", (cells, cells))
    small.putdata([seed.randint(low, high) for _ in range(cells * cells)])
    return small.resize((size, size), Image.Resampling.BICUBIC).filter(
        ImageFilter.GaussianBlur(blur)
    )


def make_fabric_texture(
    size: int,
    base_color: str,
    strength: float,
    seed: int,
) -> Image.Image:
    rng = random.Random(seed)
    base = ImageColor.getrgb(base_color)
    card = Image.new("RGBA", (size, size), (*base, 255))

    if strength <= 0:
        return card

    # Broad pulp-like tonal variation: very quiet so the swatch stays clean.
    low = soft_noise_field(size, max(3, size // 18), 108, 148, size * 0.035, rng)
    dark_alpha = low.point(lambda v: round(max(0, 127 - v) * strength * 0.12))
    light_alpha = low.point(lambda v: round(max(0, v - 127) * strength * 0.08))
    tone = Image.new("RGBA", (size, size), (120, 104, 84, 0))
    tone.putalpha(dark_alpha)
    card = Image.alpha_composite(card, tone)
    tone = Image.new("RGBA", (size, size), (255, 252, 244, 0))
    tone.putalpha(light_alpha)
    card = Image.alpha_composite(card, tone)

    # Plain-weave lines: fine, irregular, and low contrast.
    weave = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(weave)
    step = max(2, round(size / 70))
    for y in range(0, size, step):
        alpha = max(2, round(rng.randint(4, 9) * strength))
        color = (245, 239, 226, alpha) if rng.random() < 0.5 else (112, 96, 78, alpha)
        draw.line((0, y, size - 1, y + rng.choice((-1, 0, 0, 1))), fill=color, width=1)
    for x in range(0, size, step):
        alpha = max(2, round(rng.randint(3, 7) * strength))
        color = (245, 239, 226, alpha) if rng.random() < 0.5 else (112, 96, 78, alpha)
        draw.line((x, 0, x + rng.choice((-1, 0, 0, 1)), size - 1), fill=color, width=1)
    card = Image.alpha_composite(card, weave)

    # Short fibers in varied directions.
    fibers = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(fibers)
    count = max(60, size * size // 320)
    for _ in range(count):
        x = rng.randrange(size)
        y = rng.randrange(size)
        length = rng.randint(2, max(3, min(7, size // 28)))
        angle = rng.uniform(0, math.pi)
        x2 = min(size - 1, max(0, x + round(math.cos(angle) * length)))
        y2 = min(size - 1, max(0, y + round(math.sin(angle) * length)))
        alpha = max(2, round(rng.randint(8, 16) * strength))
        color = (250, 245, 233, alpha) if rng.random() < 0.55 else (104, 88, 72, alpha)
        draw.line((x, y, x2, y2), fill=color, width=1)
    card = Image.alpha_composite(card, fibers.filter(ImageFilter.GaussianBlur(0.4)))

    # Sparse neutral inclusions keep the swatch from looking digitally flat.
    flecks = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(flecks)
    for _ in range(max(10, size * size // 7000)):
        x = rng.randrange(size)
        y = rng.randrange(size)
        radius = rng.choice((1, 1, 1, 2))
        alpha = max(1, round(rng.randint(4, 9) * strength))
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(96, 82, 68, alpha),
        )
    card = Image.alpha_composite(card, flecks.filter(ImageFilter.GaussianBlur(0.5)))

    # Flat cut edge: a very faint cut line, no cloth-thickness highlight.
    edge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(edge)
    radius = max(2, round(size * 0.02))
    draw.rounded_rectangle(
        (1, 1, size - 2, size - 2),
        radius=radius,
        outline=(104, 88, 70, max(5, round(14 * strength))),
        width=1,
    )
    return Image.alpha_composite(card, edge)


def make_sheet_background(
    size: tuple[int, int],
    base_color: str,
    strength: float,
    seed: int,
) -> Image.Image:
    """Pale woven fabric page for the photo + patchwork sheet layout."""
    width, height = size
    rng = random.Random(seed)
    base = ImageColor.getrgb(base_color)
    page = Image.new("RGBA", size, (*base, 255))
    if strength <= 0:
        return page

    cell = max(12, min(width, height) // 30)
    cells_x = max(3, width // cell)
    cells_y = max(3, height // cell)
    low = Image.new("L", (cells_x, cells_y))
    low.putdata([rng.randint(108, 148) for _ in range(cells_x * cells_y)])
    low = low.resize(size, Image.Resampling.BICUBIC).filter(
        ImageFilter.GaussianBlur(cell * 0.8)
    )
    dark = Image.new("RGBA", size, (126, 104, 72, 0))
    dark.putalpha(low.point(lambda v: round(max(0, 127 - v) * strength * 0.10)))
    light = Image.new("RGBA", size, (255, 250, 230, 0))
    light.putalpha(low.point(lambda v: round(max(0, v - 127) * strength * 0.07)))
    page = Image.alpha_composite(page, dark)
    page = Image.alpha_composite(page, light)

    weave = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(weave)
    step = max(3, min(width, height) // 250)
    for y in range(0, height, step):
        alpha = max(2, round(rng.randint(4, 8) * strength))
        color = (255, 250, 235, alpha) if rng.random() < 0.5 else (120, 96, 68, alpha)
        draw.line((0, y, width - 1, y + rng.choice((-1, 0, 0, 1))), fill=color)
    for x in range(0, width, step):
        alpha = max(2, round(rng.randint(3, 7) * strength))
        color = (255, 250, 235, alpha) if rng.random() < 0.5 else (120, 96, 68, alpha)
        draw.line((x, 0, x + rng.choice((-1, 0, 0, 1)), height - 1), fill=color)
    page = Image.alpha_composite(page, weave)

    fibers = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(fibers)
    count = max(240, width * height // 1400)
    for _ in range(count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        length = rng.randint(2, 7)
        angle = rng.uniform(0, math.pi)
        x2 = min(width - 1, max(0, x + round(math.cos(angle) * length)))
        y2 = min(height - 1, max(0, y + round(math.sin(angle) * length)))
        alpha = max(2, round(rng.randint(6, 13) * strength))
        color = (255, 250, 235, alpha) if rng.random() < 0.55 else (112, 90, 64, alpha)
        draw.line((x, y, x2, y2), fill=color)
    return Image.alpha_composite(page, fibers.filter(ImageFilter.GaussianBlur(0.4)))


def stitch_segment(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[int, int, int, int],
    width: int,
    dash: int,
    gap: int,
    rng: random.Random,
) -> None:
    sx, sy = start
    ex, ey = end
    dx, dy = ex - sx, ey - sy
    length = math.hypot(dx, dy)
    if length <= 0:
        return
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    cursor = 0.0
    while cursor < length:
        segment = min(dash * rng.uniform(0.75, 1.25), length - cursor)
        jitter_a = rng.choice((-1, 0, 0, 1))
        jitter_b = rng.choice((-1, 0, 0, 1))
        ax = sx + ux * cursor + px * jitter_a
        ay = sy + uy * cursor + py * jitter_a
        bx = sx + ux * (cursor + segment) + px * jitter_b
        by = sy + uy * (cursor + segment) + py * jitter_b
        draw.line((ax, ay, bx, by), fill=color, width=width)
        cursor += segment + gap * rng.uniform(0.7, 1.3)


def draw_sheet_frame(
    canvas: Image.Image,
    color: str,
    inset: int,
    width: int,
    seed: int,
) -> None:
    rgb = ImageColor.getrgb(color)
    draw = ImageDraw.Draw(canvas, "RGBA")
    draw.rectangle(
        (inset, inset, canvas.width - 1 - inset, canvas.height - 1 - inset),
        outline=(*rgb, 225),
        width=width,
    )
    rng = random.Random(seed)
    inner = inset + max(4, width * 2)
    left, top = inner, inner
    right, bottom = canvas.width - 1 - inner, canvas.height - 1 - inner
    dash = max(4, round(min(canvas.size) * 0.022))
    gap = max(3, round(dash * 0.8))
    stitch_color = (*rgb, 190)
    stitch_segment(draw, (left, top), (right, top), stitch_color, width, dash, gap, rng)
    stitch_segment(draw, (right, top), (right, bottom), stitch_color, width, dash, gap, rng)
    stitch_segment(draw, (right, bottom), (left, bottom), stitch_color, width, dash, gap, rng)
    stitch_segment(draw, (left, bottom), (left, top), stitch_color, width, dash, gap, rng)


def draw_photo_stitch(
    canvas: Image.Image,
    photo_box: tuple[int, int, int, int],
    color: str,
    width: int,
    offset: int,
    seed: int,
) -> None:
    rgb = ImageColor.getrgb(color)
    draw = ImageDraw.Draw(canvas, "RGBA")
    x0, y0, x1, y1 = photo_box
    left, top, right, bottom = x0 - offset, y0 - offset, x1 + offset, y1 + offset
    rng = random.Random(seed)
    dash = max(4, round(min(canvas.size) * 0.018))
    gap = max(3, round(dash * 0.85))
    stitch_color = (*rgb, 220)
    stitch_segment(draw, (left, top), (right, top), stitch_color, width, dash, gap, rng)
    stitch_segment(draw, (right, top), (right, bottom), stitch_color, width, dash, gap, rng)
    stitch_segment(draw, (right, bottom), (left, bottom), stitch_color, width, dash, gap, rng)
    stitch_segment(draw, (left, bottom), (left, top), stitch_color, width, dash, gap, rng)


def add_stitch_border(
    card: Image.Image,
    inset: int,
    color: tuple[int, int, int, int],
    width: int,
    seed: int,
) -> None:
    rng = random.Random(seed)
    size = card.width
    draw = ImageDraw.Draw(card, "RGBA")
    left, top = inset, inset
    right, bottom = size - 1 - inset, size - 1 - inset
    dash = max(3, round(size * 0.03))
    gap = max(2, round(dash * 0.75))
    stitch_segment(draw, (left, top), (right, top), color, width, dash, gap, rng)
    stitch_segment(draw, (right, top), (right, bottom), color, width, dash, gap, rng)
    stitch_segment(draw, (right, bottom), (left, bottom), color, width, dash, gap, rng)
    stitch_segment(draw, (left, bottom), (left, top), color, width, dash, gap, rng)


def fit_motif(
    motif: Image.Image,
    max_width: int,
    max_height: int,
    sharpen: float = 0.0,
) -> Image.Image:
    scale = min(max_width / motif.width, max_height / motif.height)
    width = max(1, round(motif.width * scale))
    height = max(1, round(motif.height * scale))
    resized = motif.resize((width, height), Image.Resampling.LANCZOS)
    if sharpen > 0 and scale < 0.95:
        rgb = resized.convert("RGB").filter(
            ImageFilter.UnsharpMask(
                radius=1.0,
                percent=round(45 * sharpen),
                threshold=3,
            )
        )
        resized = Image.merge("RGBA", (*rgb.split(), resized.getchannel("A")))
    return resized


def load_font(path: Path | None, size: int, text: str) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path is not None:
        return ImageFont.truetype(str(path), size)
    candidates = CJK_FONTS if any(ord(ch) > 127 for ch in text) else LATIN_FONTS
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default(size=size)


def draw_caption(
    card: Image.Image,
    caption: str,
    args: argparse.Namespace,
) -> None:
    band = max(16, round(card.width * 0.15))
    if args.caption_size > 0:
        size = args.caption_size
    else:
        size = max(8, round(band * 0.56))
    font = load_font(args.font, size, caption)
    limit = round(card.width * 0.86)
    while size > 8:
        bbox = ImageDraw.Draw(card).textbbox((0, 0), caption, font=font)
        if bbox[2] - bbox[0] <= limit:
            break
        size -= 1
        font = load_font(args.font, size, caption)
    color = ImageColor.getrgb(args.caption_color)
    draw = ImageDraw.Draw(card)
    center_x = card.width // 2
    center_y = card.height - band // 2
    draw.text(
        (center_x, center_y),
        caption,
        font=font,
        fill=(*color, 255),
        anchor="mm",
    )


def shadow_layer(
    canvas_size: tuple[int, int],
    mask: Image.Image,
    position: tuple[int, int],
    blur: float,
    opacity: float,
) -> Image.Image:
    alpha = Image.new("L", canvas_size, 0)
    alpha.paste(mask, position)
    alpha = alpha.filter(ImageFilter.GaussianBlur(blur))
    alpha = alpha.point(lambda value: round(value * opacity))
    shadow = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    shadow.putalpha(alpha)
    return shadow


def apply_shadow(
    canvas: Image.Image,
    mask: Image.Image,
    position: tuple[int, int],
    size: int,
    mode: str,
) -> tuple[Image.Image, int]:
    """Add no shadow, a hairline contact shadow, or a restrained soft shadow."""
    if mode == "none":
        return canvas, 0
    if mode == "hairline":
        blur = max(1, round(size * 0.004))
        layer = shadow_layer(
            canvas.size,
            mask,
            (position[0], position[1] + 1),
            blur=blur,
            opacity=0.16,
        )
        return Image.alpha_composite(canvas, layer), math.ceil(blur * 3) + 3
    ambient_blur = max(2, round(size * 0.03))
    contact_blur = max(1, round(size * 0.006))
    ambient = shadow_layer(
        canvas.size,
        mask,
        (position[0], position[1] + max(1, round(size * 0.01))),
        blur=ambient_blur,
        opacity=0.18,
    )
    contact = shadow_layer(
        canvas.size,
        mask,
        (position[0], position[1] + 1),
        blur=contact_blur,
        opacity=0.26,
    )
    canvas = Image.alpha_composite(canvas, ambient)
    canvas = Image.alpha_composite(canvas, contact)
    return canvas, math.ceil(max(ambient_blur, contact_blur) * 3) + 6


def print_plan(
    args: argparse.Namespace,
    layout: Layout,
    motif_size: tuple[int, int] | None = None,
    fit_size: tuple[int, int] | None = None,
) -> None:
    width, height = layout.photo_size
    print(f"PHOTO={args.photo}")
    print(f"PHOTO_SIZE=({width}, {height})")
    print(f"PHOTO_SHORT_SIDE={min(width, height)}")
    print(
        "PHOTO_RESOLUTION_NOTE="
        + ("low-resolution-avoid-upscaling" if min(width, height) < 800 else "ok")
    )
    print(f"FINAL_SIZE=({width}, {height})")
    print(f"CORNER={layout.corner}")
    print(f"PLACEMENT={layout.placement}")
    print(f"PLACEMENT_BOX={layout.box}")
    print(f"PLACEMENT_SIZE_PX={layout.box_size}")
    if layout.placement == "card":
        print(f"CARD_STYLE={args.card_style}")
        print(f"CARD_BOX={layout.box}")
        print(f"CARD_SIZE_PX={layout.box_size}")
        print(f"CARD_FRACTION={args.card_fraction:.6f}")
    else:
        print(f"PLACEMENT_FRACTION={args.motif_size_fraction:.6f}")
    print(f"MARGIN_PX={layout.margin}")
    print(f"MARGIN_FRACTION={args.margin_fraction:.6f}")
    print(f"MOTIF_FRACTION={args.motif_fraction:.6f}")
    print(f"MOTIF_MODE={'transparent-rgba' if args.motif else 'pending'}")
    print(f"MOTIF_TRIMMED_SIZE={motif_size if motif_size else 'pending'}")
    print(f"MOTIF_FIT={fit_size if fit_size else 'pending'}")
    print(f"MOTIF_SHARPEN={args.motif_sharpen:.2f}")
    print(f"SHADOW={args.shadow}")
    print("PHOTO_PIXEL_VALUES=unchanged")
    print(f"CAPTION={args.caption!r}")
    print(f"OUTPUT={args.output}")


def print_sheet_plan(
    args: argparse.Namespace,
    layout: SheetLayout,
    motif_size: tuple[int, int] | None = None,
    fit_size: tuple[int, int] | None = None,
) -> None:
    width, height = layout.photo_size
    canvas_w, canvas_h = layout.canvas_size
    photo_w = layout.photo_box[2] - layout.photo_box[0]
    photo_h = layout.photo_box[3] - layout.photo_box[1]
    patch_w = layout.patch_box[2] - layout.patch_box[0]
    patch_h = layout.patch_box[3] - layout.patch_box[1]
    print(f"PHOTO={args.photo}")
    print(f"PHOTO_SIZE=({width}, {height})")
    print(f"LAYOUT=sheet")
    print(f"CANVAS_SIZE=({canvas_w}, {canvas_h})")
    print(f"PHOTO_BOX={layout.photo_box}")
    print(f"PHOTO_SHARE={photo_w * photo_h / (canvas_w * canvas_h):.4f}")
    print(f"PATCH_BOX={layout.patch_box}")
    print(f"PATCH_SHARE={patch_w * patch_h / (canvas_w * canvas_h):.4f}")
    print(f"PATCH_FRACTION={args.patch_fraction:.6f}")
    print(f"SHEET_COLOR={args.sheet_color}")
    print(f"LINE_COLOR={args.line_color}")
    print(f"PHOTO_STITCH_COLOR={args.photo_stitch_color or args.line_color}")
    print(f"MARGIN_PX={layout.margin}")
    print(f"GAP_PX={layout.gap}")
    print(f"MOTIF_MODE={'transparent-rgba' if args.motif else 'pending'}")
    print(f"MOTIF_TRIMMED_SIZE={motif_size if motif_size else 'pending'}")
    print(f"MOTIF_FIT={fit_size if fit_size else 'pending'}")
    print(f"MOTIF_SHARPEN={args.motif_sharpen:.2f}")
    print("SHADOW=none")
    print("PHOTO_PIXEL_VALUES=unchanged")
    print(f"CAPTION={args.caption!r}")
    print(f"OUTPUT={args.output}")


def compose_sheet(
    photo: Image.Image,
    motif: Image.Image,
    layout: SheetLayout,
    args: argparse.Namespace,
) -> tuple[Image.Image, tuple[int, int], tuple[int, int, int, int]]:
    canvas = make_sheet_background(
        layout.canvas_size,
        args.sheet_color,
        args.texture_strength,
        seed=args.seed + 100,
    )
    short = min(layout.canvas_size)
    line_width = max(1, round(short / 500))
    frame_inset = max(4, round(layout.margin * 0.35))
    draw_sheet_frame(
        canvas,
        args.line_color,
        frame_inset,
        line_width,
        seed=args.seed + 11,
    )

    x0, y0, _, _ = layout.photo_box
    canvas.alpha_composite(photo.convert("RGBA"), (x0, y0))
    photo_stitch_color = args.photo_stitch_color or args.line_color
    photo_stitch_width = args.photo_stitch_width or max(
        1, round(min(photo.size) / 500)
    )
    draw_photo_stitch(
        canvas,
        layout.photo_box,
        photo_stitch_color,
        photo_stitch_width,
        offset=max(3, round(layout.margin * 0.35)),
        seed=args.seed + 23,
    )

    px0, py0, px1, py1 = layout.patch_box
    patch_w, patch_h = px1 - px0, py1 - py0
    pad = max(6, round(min(patch_w, patch_h) * 0.08))
    fitted = fit_motif(
        motif,
        max(8, patch_w - 2 * pad),
        max(8, patch_h - 2 * pad),
        sharpen=args.motif_sharpen,
    )
    mx = px0 + (patch_w - fitted.width) // 2
    my = py0 + (patch_h - fitted.height) // 2
    canvas.alpha_composite(fitted, (mx, my))
    return canvas.convert("RGB"), fitted.size, (mx, my, mx + fitted.width, my + fitted.height)


def compose(
    photo: Image.Image,
    motif: Image.Image,
    layout: Layout,
    args: argparse.Namespace,
) -> tuple[Image.Image, tuple[int, int, int, int], tuple[int, int], tuple[int, int]]:
    width, height = photo.size
    x0, y0, x1, y1 = layout.box
    box_size = layout.box_size

    if layout.placement == "direct":
        fitted = fit_motif(motif, box_size, box_size, sharpen=args.motif_sharpen)
        mx = x0 + (box_size - fitted.width) // 2
        my = y0 + (box_size - fitted.height) // 2
        alpha = fitted.getchannel("A")
        canvas = photo.convert("RGBA")
        canvas, spread = apply_shadow(
            canvas,
            alpha,
            (mx, my),
            max(24, fitted.width),
            args.shadow,
        )
        canvas.alpha_composite(fitted, (mx, my))
        affected = (
            mx - spread - 2,
            my - spread - 2,
            mx + fitted.width + spread + 2,
            my + fitted.height + spread + 2,
        )
        return canvas.convert("RGB"), affected, motif.size, fitted.size

    card_size = box_size
    size_factor = min(1.0, max(0.55, card_size / 200))
    strength = (
        args.texture_strength
        * size_factor
        * (1.0 if args.card_style == "linen" else 0.35)
    )
    card = make_fabric_texture(
        card_size,
        args.card_color,
        strength,
        seed=args.seed + card_size,
    )
    mask = rounded_mask(card_size, max(2, round(card_size * 0.02)))
    card.putalpha(mask)

    stitch_inset = max(3, round(card_size * 0.035))
    stitch_width = args.stitch_width or max(1, round(card_size / 180))
    stitch_color = ImageColor.getrgb(args.stitch_color)
    add_stitch_border(
        card,
        inset=stitch_inset,
        color=(*stitch_color, 235),
        width=stitch_width,
        seed=args.seed + 7,
    )

    band = max(16, round(card_size * 0.14)) if args.caption else 0
    pad = max(4, round(card_size * 0.05))
    target = round(card_size * math.sqrt(args.motif_fraction))
    avail_w = max(8, min(card_size - 2 * pad, target))
    avail_h = max(8, min(card_size - 2 * pad - band, target))
    fitted = fit_motif(motif, avail_w, avail_h, sharpen=args.motif_sharpen)
    mx = (card_size - fitted.width) // 2
    my = pad + max(0, (avail_h - fitted.height) // 2)
    card.alpha_composite(fitted, (mx, my))

    if args.caption:
        draw_caption(card, args.caption, args)

    canvas = photo.convert("RGBA")
    canvas, spread = apply_shadow(canvas, mask, (x0, y0), card_size, args.shadow)
    canvas.alpha_composite(card, (x0, y0))

    affected = (x0 - spread - 2, y0 - spread - 2, x1 + spread + 2, y1 + spread + 2)
    return canvas.convert("RGB"), affected, motif.size, fitted.size


def verify_photo_pixels(
    original: Image.Image,
    output: Image.Image,
    allowed: tuple[int, int, int, int],
) -> None:
    diff = ImageChops.difference(original, output).copy()
    ImageDraw.Draw(diff).rectangle(allowed, fill=(0, 0, 0))
    leftover = diff.getbbox()
    if leftover is not None:
        raise RuntimeError(
            "photo pixels changed outside the placement/shadow area at "
            f"{leftover}; the compositor must not alter the source photo"
        )


def verify_sheet_photo(
    original: Image.Image,
    output: Image.Image,
    photo_box: tuple[int, int, int, int],
) -> None:
    rendered = output.crop(photo_box)
    difference = ImageChops.difference(original, rendered).getbbox()
    if difference is not None:
        raise RuntimeError(
            f"photo panel differs from the source at {difference}; "
            "the sheet layout must preserve photo pixels exactly"
        )


def main() -> None:
    args = parse_args()
    validate(args)
    photo = Image.open(args.photo).convert("RGB")
    if min(photo.size) < 800:
        print(
            f"warning: photo short side is {min(photo.size)} px; "
            "the compositor will not upscale it. Export a larger original "
            "for a crisp final image.",
            file=sys.stderr,
        )
    args.output = args.output or args.photo.with_name(
        f"{args.photo.stem}-patchwork.png"
    )

    if args.placement == "sheet":
        sheet = resolve_sheet_layout(photo.size, args.patch_fraction)
        if args.plan:
            motif_size = None
            fit_size = None
            if args.motif is not None:
                preview = load_motif(args.motif)
                motif_size = preview.size
                px0, py0, px1, py1 = sheet.patch_box
                patch_w, patch_h = px1 - px0, py1 - py0
                pad = max(6, round(min(patch_w, patch_h) * 0.08))
                fit_size = fit_motif(
                    preview,
                    max(8, patch_w - 2 * pad),
                    max(8, patch_h - 2 * pad),
                    sharpen=args.motif_sharpen,
                ).size
            print_sheet_plan(args, sheet, motif_size=motif_size, fit_size=fit_size)
            return

        motif = load_motif(args.motif)
        output, fit_size, _ = compose_sheet(photo, motif, sheet, args)
        verify_sheet_photo(photo, output, sheet.photo_box)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output.save(args.output, format="PNG", optimize=True)
        print_sheet_plan(args, sheet, motif_size=motif.size, fit_size=fit_size)
        return

    box_fraction = (
        args.motif_size_fraction
        if args.placement == "direct"
        else args.card_fraction
    )
    layout = resolve_layout(
        photo.size,
        args.corner,
        args.placement,
        box_fraction,
        args.margin_fraction,
    )

    if args.plan:
        motif_size = None
        fit_size = None
        if args.motif is not None:
            preview = load_motif(args.motif)
            motif_size = preview.size
            if layout.placement == "direct":
                fit_size = fit_motif(
                    preview,
                    layout.box_size,
                    layout.box_size,
                    sharpen=args.motif_sharpen,
                ).size
            else:
                band = max(16, round(layout.box_size * 0.14)) if args.caption else 0
                pad = max(4, round(layout.box_size * 0.05))
                target = round(layout.box_size * math.sqrt(args.motif_fraction))
                fit_size = fit_motif(
                    preview,
                    max(8, min(layout.box_size - 2 * pad, target)),
                    max(8, min(layout.box_size - 2 * pad - band, target)),
                    sharpen=args.motif_sharpen,
                ).size
        print_plan(args, layout, motif_size=motif_size, fit_size=fit_size)
        return

    motif = load_motif(args.motif)
    output, affected, motif_size, fit_size = compose(photo, motif, layout, args)
    verify_photo_pixels(photo, output, affected)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, format="PNG", optimize=True)

    print_plan(args, layout, motif_size=motif_size, fit_size=fit_size)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error
