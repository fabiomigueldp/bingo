from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = ROOT / "public"
ICON_DIR = PUBLIC_DIR / "icons"
SCREENSHOT_DIR = PUBLIC_DIR / "screenshots"
SPLASH_DIR = PUBLIC_DIR / "splash"

PAPER = "#f4efe7"
PAPER_DEEP = "#ebe1d1"
SURFACE = "#fffaf1"
INK = "#2d2a26"
MUTED = "#7a6d5c"
GOLD = "#b99546"
RED = "#a84f3d"
PLUM = "#6e536f"
TEAL = "#2f6e70"
GREEN = "#64703c"


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for name in names:
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def text_center(draw: ImageDraw.ImageDraw, xy, text: str, fill: str, size: int, bold: bool = False) -> None:
    fnt = font(size, bold)
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (box[2] - box[0]) / 2, xy[1] - (box[3] - box[1]) / 2), text, fill=fill, font=fnt)


def rounded_rectangle(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_app_mark(draw: ImageDraw.ImageDraw, scale: float, offset=(0, 0)) -> None:
    ox, oy = offset

    def s(value):
        return int(round(value * scale))

    def box(x1, y1, x2, y2):
        return (ox + s(x1), oy + s(y1), ox + s(x2), oy + s(y2))

    rounded_rectangle(draw, box(116, 94, 396, 418), s(34), SURFACE, GOLD, s(12))
    rounded_rectangle(draw, box(144, 126, 368, 190), s(18), INK)

    dots = [
        (178, 236, GOLD),
        (256, 236, RED),
        (334, 236, PLUM),
        (178, 308, TEAL),
        (256, 308, GREEN),
        (334, 308, GOLD),
    ]
    for x, y, color in dots:
        draw.ellipse(box(x - 17, y - 17, x + 17, y + 17), fill=color)

    draw.line((ox + s(170), oy + s(362), ox + s(342), oy + s(362)), fill=INK, width=s(18))
    draw.line((ox + s(181), oy + s(155), ox + s(331), oy + s(155)), fill=SURFACE, width=s(18))


def make_icon(size: int, path: Path, maskable: bool = False) -> None:
    img = Image.new("RGBA", (size, size), PAPER)
    draw = ImageDraw.Draw(img)
    scale = (size * (0.78 if maskable else 1.0)) / 512
    mark_size = int(512 * scale)
    offset = ((size - mark_size) // 2, (size - mark_size) // 2)
    draw_app_mark(draw, scale, offset)
    img.convert("RGB").save(path)


def make_favicons() -> None:
    make_icon(16, PUBLIC_DIR / "favicon-16x16.png")
    make_icon(32, PUBLIC_DIR / "favicon-32x32.png")
    sizes = [(16, 16), (32, 32), (48, 48)]
    frames = []
    for size, _ in sizes:
        img = Image.new("RGBA", (size, size), PAPER)
        draw_app_mark(ImageDraw.Draw(img), size / 512)
        frames.append(img.convert("RGBA"))
    frames[0].save(PUBLIC_DIR / "favicon.ico", sizes=sizes, append_images=frames[1:])


def make_screenshot(path: Path, width: int, height: int, tablet: bool = False) -> None:
    img = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)
    margin = int(width * (0.07 if tablet else 0.055))
    max_card = int(width * (0.58 if tablet else 0.78))
    card_w = min(max_card, width - margin * 2)
    card_h = int(card_w * 1.42)
    card_x = (width - card_w) // 2
    card_y = int(height * (0.28 if tablet else 0.25))

    draw.rectangle((0, 0, width, height), fill=PAPER)
    for y in range(0, height, max(8, height // 120)):
        blend = y / height
        tone = int(239 - blend * 10)
        draw.line((0, y, width, y), fill=(244, max(225, tone), max(210, tone - 12)))

    text_center(draw, (width // 2, int(height * 0.10)), "Bingo", INK, int(width * (0.095 if tablet else 0.13)), True)
    text_center(
        draw,
        (width // 2, int(height * 0.145)),
        "Violência e discriminação",
        MUTED,
        int(width * (0.024 if tablet else 0.035)),
        True,
    )

    shadow = int(width * 0.016)
    rounded_rectangle(draw, (card_x + shadow, card_y + shadow, card_x + card_w + shadow, card_y + card_h + shadow), int(card_w * 0.08), "#d8cbb8")
    rounded_rectangle(draw, (card_x, card_y, card_x + card_w, card_y + card_h), int(card_w * 0.08), SURFACE, GOLD, max(3, int(card_w * 0.012)))
    rounded_rectangle(draw, (card_x, card_y, card_x + card_w, card_y + int(card_h * 0.045)), int(card_w * 0.08), GOLD)

    chip_w = int(card_w * 0.24)
    chip_h = int(card_w * 0.13)
    rounded_rectangle(draw, (card_x + int(card_w * 0.08), card_y + int(card_h * 0.08), card_x + int(card_w * 0.08) + chip_w, card_y + int(card_h * 0.08) + chip_h), chip_h // 2, GOLD)
    text_center(draw, (card_x + int(card_w * 0.08) + chip_w // 2, card_y + int(card_h * 0.08) + chip_h // 2), "B12", SURFACE, int(card_w * 0.065), True)

    text_center(draw, (width // 2, card_y + int(card_h * 0.28)), "Respeito", INK, int(card_w * 0.105), True)
    lines = [
        "Conduza a rodada, leia o caso",
        "e acompanhe as cartelas em jogo.",
        "Funciona instalado e offline.",
    ]
    for index, line in enumerate(lines):
        text_center(draw, (width // 2, card_y + int(card_h * 0.42) + index * int(card_w * 0.075)), MUTED and line, MUTED, int(card_w * 0.044), False)

    ball_y = card_y + int(card_h * 0.68)
    colors = [GOLD, RED, PLUM, TEAL, GREEN]
    for index, color in enumerate(colors):
        cx = width // 2 + (index - 2) * int(card_w * 0.14)
        r = int(card_w * 0.045)
        draw.ellipse((cx - r, ball_y - r, cx + r, ball_y + r), fill=color)

    button_w = int(card_w * 0.72)
    button_h = int(card_w * 0.14)
    button_x = (width - button_w) // 2
    button_y = card_y + int(card_h * 0.82)
    rounded_rectangle(draw, (button_x, button_y, button_x + button_w, button_y + button_h), button_h // 2, GOLD)
    text_center(draw, (width // 2, button_y + button_h // 2), "Iniciar jogo", SURFACE, int(card_w * 0.044), True)
    img.save(path, quality=92)


def make_splash(path: Path, width: int, height: int) -> None:
    img = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(img)
    mark_size = int(min(width, height) * 0.24)
    mark = Image.new("RGBA", (mark_size, mark_size), (0, 0, 0, 0))
    draw_app_mark(ImageDraw.Draw(mark), mark_size / 512)
    img.paste(mark.convert("RGB"), ((width - mark_size) // 2, int(height * 0.36)), mark)
    text_center(draw, (width // 2, int(height * 0.56)), "Bingo", INK, int(width * 0.09), True)
    text_center(draw, (width // 2, int(height * 0.605)), "Violência e discriminação", MUTED, int(width * 0.032), True)
    img.save(path, quality=92)


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    SPLASH_DIR.mkdir(parents=True, exist_ok=True)

    for size in (120, 152, 167, 180, 192, 512):
        make_icon(size, ICON_DIR / f"icon-{size}.png")

    make_icon(180, ICON_DIR / "apple-touch-icon.png")
    for size in (120, 152, 167, 180):
        make_icon(size, ICON_DIR / f"apple-touch-icon-{size}x{size}.png")

    for size in (192, 512):
        make_icon(size, ICON_DIR / f"maskable-{size}.png", maskable=True)

    make_favicons()

    make_screenshot(SCREENSHOT_DIR / "iphone-portrait.png", 1290, 2796)
    make_screenshot(SCREENSHOT_DIR / "ipad-portrait.png", 2048, 2732, tablet=True)

    splash_sizes = [
        (750, 1334),
        (828, 1792),
        (1080, 2340),
        (1125, 2436),
        (1170, 2532),
        (1179, 2556),
        (1242, 2688),
        (1284, 2778),
        (1290, 2796),
        (1536, 2048),
        (1620, 2160),
        (1668, 2224),
        (1668, 2388),
        (2048, 2732),
    ]
    for width, height in splash_sizes:
        make_splash(SPLASH_DIR / f"apple-splash-{width}x{height}.png", width, height)

    print("Generated PWA assets in public/icons, public/screenshots, public/splash")


if __name__ == "__main__":
    main()
