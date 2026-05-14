from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from models.resource import Resource, ResourceStatus


class DetailView(QFrame):
    """Sag panel: secilen kaynağin detay ve düzenleme ekrani."""

    progress_updated = Signal(int, float)   # (resource_id, progress)
    status_updated = Signal(int, str)       # (resource_id, status_value)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DetailView")
        self.setMinimumWidth(280)
        self._resource_id: int | None = None

        self._build_ui()
        self._connect_signals()

        event_bus.resource_selected.connect(self._on_resource_selected)
        event_bus.theme_changed.connect(self._on_theme_changed)
        self.hide()

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # --- Header ---
        header = QHBoxLayout()
        self._title_label = QLabel("—")
        self._title_label.setObjectName("DetailTitle")
        self._title_label.setWordWrap(True)
        header.addWidget(self._title_label, stretch=1)

        self._close_btn = QPushButton()
        self._close_btn.setObjectName("DetailCloseButton")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setIcon(qta.icon(QtAwesomeIcons.CLOSE, color="#ffffff"))
        self._close_btn.setToolTip(AppStrings.CLOSE_PANEL)
        header.addWidget(self._close_btn)
        root.addLayout(header)

        # --- URL ---
        self._url_btn = QPushButton()
        self._url_btn.setObjectName("DetailUrlButton")
        self._url_btn.setFlat(True)
        self._url_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._url_btn.hide()
        root.addWidget(self._url_btn)

        # --- Durum ---
        status_row = QHBoxLayout()
        status_row.addWidget(QLabel(AppStrings.STATUS_LABEL))
        self._status_combo = QComboBox()
        self._status_combo.setObjectName("StatusCombo")
        for s in ResourceStatus:
            self._status_combo.addItem(s.value, s)
        status_row.addWidget(self._status_combo, stretch=1)
        root.addLayout(status_row)

        # --- İlerleme ---
        progress_row = QHBoxLayout()
        progress_row.addWidget(QLabel(AppStrings.PROGRESS_LABEL))
        self._progress_spin = QDoubleSpinBox()
        self._progress_spin.setObjectName("ProgressSpin")
        self._progress_spin.setRange(0.0, 100.0)
        self._progress_spin.setSingleStep(5.0)
        self._progress_spin.setSuffix(" %")
        progress_row.addWidget(self._progress_spin, stretch=1)
        root.addLayout(progress_row)

        # --- Notlar (Markdown) ---
        self._notes_edit = QTextEdit()
        self._notes_edit.setObjectName("NotesEdit")
        self._notes_edit.setPlaceholderText("Notlar (Markdown destekli)...")
        root.addWidget(self._notes_edit, stretch=1)

    def _connect_signals(self) -> None:
        self._close_btn.clicked.connect(self.hide)
        self._url_btn.clicked.connect(self._open_url)
        self._status_combo.currentIndexChanged.connect(self._on_status_changed)
        self._progress_spin.valueChanged.connect(self._on_progress_changed)

    # ------------------------------------------------------------------ #
    # Veri yükleme
    # ------------------------------------------------------------------ #

    def load_resource(self, resource: Resource) -> None:
        self._resource_id = resource.id
        self._title_label.setText(resource.title)

        if resource.url:
            self._url_btn.setText(resource.url)
            self._url_btn.setProperty("url", resource.url)
            self._url_btn.show()
        else:
            self._url_btn.hide()

        index = self._status_combo.findData(resource.status)
        if index >= 0:
            self._status_combo.blockSignals(True)
            self._status_combo.setCurrentIndex(index)
            self._status_combo.blockSignals(False)

        self._progress_spin.blockSignals(True)
        self._progress_spin.setValue(resource.progress)
        self._progress_spin.blockSignals(False)

        self._notes_edit.setPlainText(resource.content or "")
        self.show()

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_resource_selected(self, _resource_id: int) -> None:
        # Controller bu sinyali alıp load_resource çağırır;
        # burada sadece panelin görünür olduğundan emin ol.
        self.show()

    def _open_url(self) -> None:
        url = self._url_btn.property("url")
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def _on_status_changed(self) -> None:
        if self._resource_id is not None:
            status: ResourceStatus = self._status_combo.currentData()
            self.status_updated.emit(self._resource_id, status.value)

    def _on_progress_changed(self, value: float) -> None:
        if self._resource_id is not None:
            self.progress_updated.emit(self._resource_id, value)

    def _on_theme_changed(self, theme_data: dict) -> None:
        color = theme_data.get("icon_color", "#ffffff")
        self._close_btn.setIcon(qta.icon(QtAwesomeIcons.CLOSE, color=color))
