from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import piexif
from PIL import Image


class MetadataWriter:
    """Write safe generic metadata to avoid fingerprinting."""

    DEFAULT_GENERIC: Dict[str, Dict[int, bytes]] = {
        "0th": {
            piexif.ImageIFD.Make: b"Generic Camera",
            piexif.ImageIFD.Model: b"Generic Model",
            piexif.ImageIFD.Software: b"Image Scrubber",
        }
    }

    @classmethod
    def add_generic_and_save(
        cls,
        img: Image.Image,
        output_path: str | Path,
        quality: int = 95,
        extra_exif: Dict[str, Dict[int, Any]] | None = None,
    ) -> None:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)

        exif_dict = cls.DEFAULT_GENERIC.copy()
        if extra_exif:
            for ifd, data in extra_exif.items():
                exif_dict.setdefault(ifd, {}).update(data)

        try:
            exif_bytes = piexif.dump(exif_dict)
        except Exception:
            exif_bytes = b""

        img.save(
            p,
            "JPEG",
            quality=quality,
            optimize=True,
            exif=exif_bytes,
        )