from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "public" / "icons"


def rounded_rectangle(draw: ImageDraw.ImageDraw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def make_icon(size: int, path: Path) -> None:
    scale = size / 512
    img = Image.new("RGBA", (size, size), "#f4efe7")
    draw = ImageDraw.Draw(img)

    def s(value):
        return int(round(value * scale))

    rounded_rectangle(draw, (s(116), s(94), s(396), s(418)), s(34), "#fffaf1", "#b99546", s(12))
    rounded_rectangle(draw, (s(144), s(126), s(368), s(190)), s(18), "#2d2a26")

    dots = [
        (178, 236, "#b99546"),
        (256, 236, "#a84f3d"),
        (334, 236, "#6e536f"),
        (178, 308, "#2f6e70"),
        (256, 308, "#64703c"),
        (334, 308, "#b99546"),
    ]
    for x, y, color in dots:
        draw.ellipse((s(x - 17), s(y - 17), s(x + 17), s(y + 17)), fill=color)

    draw.line((s(170), s(362), s(342), s(362)), fill="#2d2a26", width=s(18))
    draw.line((s(181), s(155), s(331), s(155)), fill="#fffaf1", width=s(18))

    img.save(path)


def main() -> None:
    ICON_DIR.mkdir(parents=True, exist_ok=True)
    make_icon(192, ICON_DIR / "icon-192.png")
    make_icon(512, ICON_DIR / "icon-512.png")
    make_icon(180, ICON_DIR / "apple-touch-icon.png")
    print(f"Generated icons in {ICON_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
