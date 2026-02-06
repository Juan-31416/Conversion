from __future__ import annotations

import re
from pathlib import Path


class FilenameSanitizer:
    """Sanitize file names for SEO & privacy."""

    @staticmethod
    def sanitize(proposed_name: str) -> str:
        name = Path(proposed_name).stem.lower()

        name = re.sub(r"[^a-z0-9\s\-]", "", name)
        name = re.sub(r"[\s_]+", "-", name)
        name = re.sub(r"-{2,}", "-", name)
        name = name.strip("-")

        if not name:
            name = "image"

        return f"{name}.jpg"