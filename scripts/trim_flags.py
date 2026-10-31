from __future__ import annotations

"""Trim transparent padding around flag artwork so every flag has the same height in the UI."""

from pathlib import Path

from PIL import Image

FLAGS_DIR = Path(__file__).resolve().parent.parent / "data" / "raster" / "country_flags"


def trim(path: Path) -> bool:
    image = Image.open(path)
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    box = image.getbbox()
    if box is None:
        return False
    if box == (0, 0, image.width, image.height):
        return False
    image.crop(box).save(path)
    return True


def main() -> None:
    trimmed = 0
    for path in sorted(FLAGS_DIR.glob("*.png")):
        if trim(path):
            trimmed += 1
    print(f"trimmed {trimmed} of {len(list(FLAGS_DIR.glob('*.png')))} flags")


if __name__ == "__main__":
    main()
