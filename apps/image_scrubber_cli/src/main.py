from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from packages.image_scrubber_core.metadata.cleaner import MetadataCleaner
from packages.image_scrubber_core.metadata.writer import MetadataWriter
from packages.image_scrubber_core.filenames.sanitizer import FilenameSanitizer
from packages.image_scrubber_core.security.hashing import FileHasher

app = typer.Typer(help="CLI para limpiar metadatos de imágenes y optimizar nombres SEO.")
console = Console()


@app.command()
def scrub(
    input_path: Path = typer.Argument(..., exists=True, readable=True, help="Imagen de entrada"),
    output_dir: Optional[Path] = typer.Option(
        None, "--output-dir", "-o", help="Directorio de salida (por defecto, mismo que la imagen)"
    ),
    name: Optional[str] = typer.Option(
        None,
        "--name",
        "-n",
        help="Nuevo nombre SEO (sin extensión). Si no se proporciona, se usa el nombre original.",
    ),
) -> None:
    """Clean EXIF metadata, add generic metadata and rename the image for SEO."""
    try:
        cleaner = MetadataCleaner()
        img, had_meta = cleaner.clean(input_path)

        proposed_name = name or input_path.stem
        sanitized = FilenameSanitizer.sanitize(proposed_name)

        out_dir = output_dir or input_path.parent
        out_path = out_dir / sanitized

        if out_path.exists():
            overwrite = typer.confirm(
                f"El archivo '{out_path.name}' ya existe. ¿Sobrescribir?", default=False
            )
            if not overwrite:
                typer.echo("Operación cancelada.")
                raise typer.Exit(code=1)

        MetadataWriter.add_generic_and_save(img, out_path)

        sha = FileHasher.sha256(out_path)

        table = Table(title="Resultado del Scrub", show_header=True, header_style="bold cyan")
        table.add_column("Campo")
        table.add_column("Valor", overflow="fold")

        table.add_row("Input", str(input_path))
        table.add_row("Output", str(out_path))
        table.add_row("Metadatos originales", "Eliminados" if had_meta else "No existían")
        table.add_row("SHA256", sha)

        console.print(table)

    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()