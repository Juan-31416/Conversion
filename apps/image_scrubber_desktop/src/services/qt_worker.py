from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from packages.image_scrubber_core.metadata.cleaner import MetadataCleaner
from packages.image_scrubber_core.filenames.sanitizer import FilenameSanitizer
from packages.image_scrubber_core.metadata.writer import MetadataWriter


class ImageProcessorWorker(QThread):
    progress = Signal(str)
    finished = Signal(str, bool)
    error = Signal(str)

    def __init__(self, image_path: str, new_filename: str, output_directory: str | None):
        super().__init__()
        self.image_path = image_path
        self.new_filename = new_filename
        self.output_directory = output_directory

    def run(self) -> None:
        try:
            self.progress.emit("Limpiando metadatos…")
            cleaner = MetadataCleaner()
            img, had_meta = cleaner.clean(self.image_path)

            self.progress.emit("Generando nombre…")
            sanitized = FilenameSanitizer.sanitize(self.new_filename)

            out_dir = Path(self.output_directory or Path(self.image_path).parent)
            out_path = out_dir / sanitized

            self.progress.emit("Guardando imagen...")
            MetadataWriter.add_generic_and_save(img, out_path)

            self.finished.emit(str(out_path), had_meta)

        except Exception as exc:  # pragma: no cover - defensive
            self.error.emit(str(exc))