from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from api.routes_images import router as images_router
from core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_name,
        version=settings.api_version,
        description="API para limpiar metadatos de imágenes y optimizar nombres SEO.",
    )

    app.include_router(images_router)
    return app


app = create_app()


def run() -> None:
    uvicorn.run("image_scrubber_api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()