from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    api_name: str = "image-scrubber-api"
    api_version: str = "0.1.0"
    storage_dir: Path = Path("/tmp/image_scrubber_api_storage").resolve()

    class Config:
        frozen = True


settings = Settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)