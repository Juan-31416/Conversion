from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from fastapi.responses import FileResponse

from packages.image_scrubber_core.metadata.cleaner import MetadataCleaner
from packages.image_scrubber_core.metadata.writer import MetadataWriter
from packages.image_scrubber_core.filenames.sanitizer import FilenameSanitizer
from packages.image_scrubber_core.security.hashing import FileHasher
from core.config import settings

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/scrub", response_model=dict)
async def scrub_image(
    file: Annotated[UploadFile, File(..., description="Imagen a limpiar")],
    seo_name: Annotated[str | None, Form(None, description="Nombre SEO opcional")] = None,
) -> dict:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename missing")

    original_suffix = Path(file.filename).suffix.lower()
    if original_suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato no soportado",
        )

    tmp_input = settings.storage_dir / f"upload_{file.filename}"
    with tmp_input.open("wb") as f:
        content = await file.read()
        f.write(content)

    try:
        cleaner = MetadataCleaner()
        img, had_meta = cleaner.clean(tmp_input)

        proposed = seo_name or Path(file.filename).stem
        sanitized = FilenameSanitizer.sanitize(proposed)
        output_path = settings.storage_dir / sanitized

        MetadataWriter.add_generic_and_save(img, output_path)

        sha = FileHasher.sha256(output_path)

        return {
            "output_filename": sanitized,
            "had_metadata": had_meta,
            "sha256": sha,
        }

    finally:
        if tmp_input.exists():
            tmp_input.unlink(missing_ok=True)


@router.get("/download/{filename}")
async def download_image(filename: str):
    path = settings.storage_dir / filename
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(path, filename=filename, media_type="image/jpeg")