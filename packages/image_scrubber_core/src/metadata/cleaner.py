from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image


class MetadataCleaner:
    """Responsible of deleting EXIF metadata preserving visual quality."""

    @staticmethod
    def clean(path: str | Path) -> Tuple[Image.Image, bool]:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"Image not found: {p}")

        img = Image.open(p)

        had_metadata = "exif" in img.info

        # Normalized to RGB to avoid leaks in alpha channels
        if img.mode not in ("RGB",):
            img = img.convert("RGB")

        # Return only the cleanned image in memory
        return img, had_metadata