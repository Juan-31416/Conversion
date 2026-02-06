from __future__ import annotations

import hashlib
from pathlib import Path


class FileHasher:
    """Calcula hashes criptográficos para auditoría y verificación de integridad."""

    @staticmethod
    def sha256(path: str | Path) -> str:
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"File not found: {p}")

        h = hashlib.sha256()
        with p.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()