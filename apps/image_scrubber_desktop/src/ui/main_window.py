from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QProgressBar,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QHBoxLayout,
    QFrame,
)

from packages.image_scrubber_core.filenames.sanitizer import FilenameSanitizer
from packages.image_scrubber_core.metadata.cleaner import MetadataCleaner
from packages.image_scrubber_core.metadata.writer import MetadataWriter
from packages.image_scrubber_core.security.hashing import FileHasher
from services.qt_worker import ImageProcessorWorker


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.selected_image_path: Optional[str] = None
        self.output_directory: Optional[str] = None
        self.use_same_directory: bool = True

        self._setup_window()
        self._setup_styles()
        self._build_ui()

    def _setup_window(self) -> None:
        self.setWindowTitle("Image Metadata Cleaner")
        self.setMinimumSize(650, 600)

    def _setup_styles(self) -> None:
        # Puedes cargar un styles.qss desde archivo si quieres
        pass

    def _build_ui(self) -> None:
        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("🖼️ Image Metadata Cleaner")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Limpia metadatos y optimiza tus imágenes para SEO")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666666;")
        layout.addWidget(subtitle)

        layout.addWidget(self._separator())

        layout.addWidget(self._build_image_selection_group())
        layout.addWidget(self._separator())
        layout.addWidget(self._build_config_group())
        layout.addWidget(self._separator())

        self.process_btn = QPushButton("🚀 Procesar y Guardar")
        self.process_btn.setEnabled(False)
        self.process_btn.clicked.connect(self._process_image)
        layout.addWidget(self.process_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #666666;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.setCentralWidget(central)

    def _separator(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFrameShadow(QFrame.Sunken)
        return sep

    def _build_image_selection_group(self) -> QGroupBox:
        group = QGroupBox("1. Seleccionar Imagen")
        vbox = QVBoxLayout(group)

        self.select_btn = QPushButton("📁 Elegir Imagen")
        self.select_btn.clicked.connect(self._select_image)
        vbox.addWidget(self.select_btn)

        self.image_label = QLabel("Ninguna imagen seleccionada")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("color: #666666;")
        vbox.addWidget(self.image_label)

        return group

    def _build_config_group(self) -> QGroupBox:
        group = QGroupBox("2. Configuración")
        vbox = QVBoxLayout(group)

        name_label = QLabel("Nuevo nombre (SEO):")
        vbox.addWidget(name_label)

        self.filename_entry = QLineEdit()
        self.filename_entry.setText("mi-imagen-optimizada")
        vbox.addWidget(self.filename_entry)

        hint = QLabel("💡 Usa guiones, minúsculas y palabras descriptivas")
        hint.setStyleSheet("color: #777777; font-size: 11px;")
        vbox.addWidget(hint)

        vbox.addSpacing(10)

        dir_label = QLabel("Guardar en:")
        vbox.addWidget(dir_label)

        self.same_dir_checkbox = QCheckBox("Usar mismo directorio que la imagen original")
        self.same_dir_checkbox.setChecked(True)
        self.same_dir_checkbox.stateChanged.connect(self._toggle_directory_selection)
        vbox.addWidget(self.same_dir_checkbox)

        dir_widget = QWidget()
        hbox = QHBoxLayout(dir_widget)
        hbox.setContentsMargins(0, 0, 0, 0)

        self.dir_btn = QPushButton("📂 Elegir Directorio")
        self.dir_btn.setEnabled(False)
        self.dir_btn.clicked.connect(self._select_directory)
        hbox.addWidget(self.dir_btn)

        self.dir_label = QLabel("")
        self.dir_label.setStyleSheet("color: #777777; font-size: 11px;")
        hbox.addWidget(self.dir_label)
        hbox.addStretch()

        vbox.addWidget(dir_widget)

        return group

    def _select_image(self) -> None:
        file_filter = "Imágenes (*.jpg *.jpeg *.png *.bmp *.tiff);;Todos los archivos (*.*)"
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar imagen", "", file_filter)

        if filename:
            self.selected_image_path = filename
            display_name = Path(filename).name
            if len(display_name) > 50:
                display_name = display_name[:47] + "..."

            self.image_label.setText(f"✓ {display_name}")
            self.process_btn.setEnabled(True)
            self.status_label.setText("")

    def _toggle_directory_selection(self, state: int) -> None:
        self.use_same_directory = state == Qt.Checked
        if self.use_same_directory:
            self.dir_btn.setEnabled(False)
            self.dir_label.setText("")
            self.output_directory = None
        else:
            self.dir_btn.setEnabled(True)

    def _select_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar directorio de salida")
        if directory:
            self.output_directory = directory
            disp = directory if len(directory) < 40 else "..." + directory[-37:]
            self.dir_label.setText(disp)

    def _process_image(self) -> None:
        if not self.selected_image_path:
            QMessageBox.critical(self, "Error", "Por favor selecciona una imagen")
            return

        new_name = self.filename_entry.text().strip()
        if not new_name:
            QMessageBox.critical(self, "Error", "Ingresa un nombre SEO")
            return

        if self.use_same_directory:
            output_dir = str(Path(self.selected_image_path).parent)
        else:
            if not self.output_directory:
                QMessageBox.critical(self, "Error", "Selecciona un directorio de salida")
                return
            output_dir = self.output_directory

        # Prechequeo de colisión de nombre
        sanitized = FilenameSanitizer.sanitize(new_name)
        out_path = Path(output_dir) / sanitized
        if out_path.exists():
            resp = QMessageBox.question(
                self,
                "Archivo existente",
                f"El archivo '{sanitized}' ya existe. ¿Sobrescribir?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if resp == QMessageBox.No:
                return

        self.process_btn.setEnabled(False)
        self.select_btn.setEnabled(False)
        self.progress_bar.show()
        self.status_label.setText("Procesando...")

        self.worker = ImageProcessorWorker(
            image_path=self.selected_image_path,
            new_filename=new_name,
            output_directory=output_dir,
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, msg: str) -> None:
        self.status_label.setText(msg)

    def _on_finished(self, output_path: str, had_metadata: bool) -> None:
        self.progress_bar.hide()
        self.process_btn.setEnabled(True)
        self.select_btn.setEnabled(True)

        sha = FileHasher.sha256(output_path)

        self.status_label.setText("✓ Procesado correctamente")
        QMessageBox.information(
            self,
            "Éxito",
            (
                f"Imagen guardada en:\n{output_path}\n\n"
                f"Metadatos originales: {'Eliminados' if had_metadata else 'No existían'}\n"
                f"Metadatos genéricos: Añadidos\n\n"
                f"SHA256: {sha}"
            ),
        )

    def _on_error(self, error_msg: str) -> None:
        self.progress_bar.hide()
        self.process_btn.setEnabled(True)
        self.select_btn.setEnabled(True)
        self.status_label.setText("✗ Error al procesar")
        QMessageBox.critical(self, "Error", f"Error al procesar la imagen:\n\n{error_msg}")