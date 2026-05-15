from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from core.constants.colors import Colors
from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.constants.status import status_label
from core.events import event_bus
from models import Resource, ResourceStatus
from ui.components.resource_form import ResourceForm
from ui.theme_utils import resolve_theme_color

_PAGE_EMPTY = 0
_PAGE_VIEW = 1
_PAGE_FORM = 2


class DetailView(QFrame):
    """Sag panel: bos / kaynak detay / kaynak formu."""

    progress_updated = Signal(int, int)
    status_updated = Signal(int, object)   # (resource_id, ResourceStatus enum)
    content_updated = Signal(int, str)     # (resource_id, notes text)
    form_submitted = Signal(dict)          # ResourceForm → MainWindow
    edit_requested = Signal(int)           # resource_id
    delete_requested = Signal(int)         # resource_id

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DetailView")
        self.setMinimumWidth(280)
        self._resource_id: int | None = None
        self._delete_confirm: bool = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        self._stack.addWidget(self._build_empty_page())   # 0
        self._stack.addWidget(self._build_view_page())    # 1
        self._form_page = ResourceForm()
        self._stack.addWidget(self._form_page)             # 2

        self._connect_signals()
        event_bus.theme_changed.connect(self._on_theme_changed)
        self.hide()

    # ------------------------------------------------------------------ #
    # Sayfa insa
    # ------------------------------------------------------------------ #

    def _build_empty_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        lbl = QLabel("Bir kaynak seçin\nveya 'Yeni Ekle'ye basın.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setObjectName("EmptyDetailLabel")
        layout.addWidget(lbl)
        return w

    def _build_view_page(self) -> QWidget:
        w = QWidget()
        root = QVBoxLayout(w)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        header = QHBoxLayout()
        self._title_label = QLabel("—")
        self._title_label.setObjectName("DetailTitle")
        self._title_label.setWordWrap(True)
        header.addWidget(self._title_label, stretch=1)

        self._close_btn = QPushButton()
        self._close_btn.setObjectName("DetailCloseButton")
        self._close_btn.setFixedSize(28, 28)
        self._close_btn.setIcon(
            qta.icon(QtAwesomeIcons.CLOSE, color=resolve_theme_color(None, Colors.ICON))
        )
        self._close_btn.setToolTip(AppStrings.CLOSE_PANEL)
        header.addWidget(self._close_btn)
        root.addLayout(header)

        self._url_btn = QPushButton()
        self._url_btn.setObjectName("DetailUrlButton")
        self._url_btn.setFlat(True)
        self._url_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._url_btn.hide()
        root.addWidget(self._url_btn)

        status_row = QHBoxLayout()
        status_row.addWidget(QLabel(AppStrings.STATUS_LABEL))
        self._status_combo = QComboBox()
        self._status_combo.setObjectName("StatusCombo")
        for s in ResourceStatus:
            self._status_combo.addItem(status_label(s), s)
        status_row.addWidget(self._status_combo, stretch=1)
        root.addLayout(status_row)

        progress_row = QHBoxLayout()
        progress_row.addWidget(QLabel(AppStrings.PROGRESS_LABEL))
        self._progress_spin = QSpinBox()
        self._progress_spin.setObjectName("ProgressSpin")
        self._progress_spin.setRange(0, 100)
        self._progress_spin.setSingleStep(5)
        self._progress_spin.setSuffix(" %")
        progress_row.addWidget(self._progress_spin, stretch=1)
        root.addLayout(progress_row)

        self._notes_edit = QTextEdit()
        self._notes_edit.setObjectName("NotesEdit")
        self._notes_edit.setPlaceholderText("Notlar (Markdown destekli)...")
        root.addWidget(self._notes_edit, stretch=1)

        self._save_notes_btn = QPushButton(AppStrings.SAVE_NOTES)
        self._save_notes_btn.setObjectName("SaveNotesButton")
        root.addWidget(self._save_notes_btn)

        action_row = QHBoxLayout()
        self._edit_btn = QPushButton(AppStrings.EDIT_RESOURCE)
        self._edit_btn.setObjectName("EditResourceButton")
        self._delete_btn = QPushButton(AppStrings.DELETE_RESOURCE)
        self._delete_btn.setObjectName("DeleteResourceButton")
        action_row.addWidget(self._edit_btn)
        action_row.addWidget(self._delete_btn)
        root.addLayout(action_row)

        self._delete_confirm_btn = QPushButton(AppStrings.CONFIRM_DELETE_RESOURCE)
        self._delete_confirm_btn.setObjectName("DeleteResourceConfirmButton")
        self._delete_confirm_btn.hide()
        root.addWidget(self._delete_confirm_btn)

        return w

    # ------------------------------------------------------------------ #
    # Sinyal baglantilari
    # ------------------------------------------------------------------ #

    def _connect_signals(self) -> None:
        self._close_btn.clicked.connect(self.clear)
        self._url_btn.clicked.connect(self._open_url)
        self._status_combo.currentIndexChanged.connect(self._on_status_changed)
        self._progress_spin.valueChanged.connect(self._on_progress_changed)
        self._save_notes_btn.clicked.connect(self._on_save_notes)
        self._edit_btn.clicked.connect(self._on_edit_clicked)
        self._delete_btn.clicked.connect(self._on_delete_first_click)
        self._delete_confirm_btn.clicked.connect(self._on_delete_confirmed)
        self._form_page.submitted.connect(self.form_submitted)
        self._form_page.cancelled.connect(self.clear)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def load_resource(self, resource: Resource) -> None:
        self._resource_id = resource.id
        self._delete_confirm = False
        self._delete_confirm_btn.hide()
        self._delete_btn.setText(AppStrings.DELETE_RESOURCE)
        self._delete_btn.setObjectName("DeleteResourceButton")
        self._delete_btn.style().unpolish(self._delete_btn)
        self._delete_btn.style().polish(self._delete_btn)

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
        self._progress_spin.setValue(int(resource.progress))
        self._progress_spin.blockSignals(False)

        self._notes_edit.setPlainText(resource.content or "")
        self._stack.setCurrentIndex(_PAGE_VIEW)
        self.show()

    def current_resource_id(self) -> int | None:
        return self._resource_id

    def show_form(self, categories: list) -> None:
        """Yeni kaynak ekleme formu."""
        self._form_page.reset_for_new()
        self._form_page.load_categories(categories)
        self._stack.setCurrentIndex(_PAGE_FORM)
        self.show()

    def show_form_edit(self, resource: Resource, categories: list) -> None:
        """Mevcut kaynak duzenleme formu."""
        self._form_page.load_resource(resource, categories)
        self._stack.setCurrentIndex(_PAGE_FORM)
        self.show()

    def clear(self) -> None:
        self._resource_id = None
        self._delete_confirm = False
        self._stack.setCurrentIndex(_PAGE_EMPTY)
        self.hide()

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _open_url(self) -> None:
        url = self._url_btn.property("url")
        if url:
            QDesktopServices.openUrl(QUrl(url))

    def _on_status_changed(self) -> None:
        if self._resource_id is not None:
            status: ResourceStatus = self._status_combo.currentData()
            self.status_updated.emit(self._resource_id, status)

    def _on_progress_changed(self, value: int) -> None:
        if self._resource_id is not None:
            self.progress_updated.emit(self._resource_id, value)

    def _on_save_notes(self) -> None:
        if self._resource_id is not None:
            text = self._notes_edit.toPlainText()
            self.content_updated.emit(self._resource_id, text)

    def _on_edit_clicked(self) -> None:
        if self._resource_id is not None:
            self.edit_requested.emit(self._resource_id)

    def _on_delete_first_click(self) -> None:
        self._delete_confirm = True
        self._delete_confirm_btn.show()
        self._delete_btn.hide()

    def _on_delete_confirmed(self) -> None:
        if self._resource_id is not None:
            self.delete_requested.emit(self._resource_id)

    def _on_theme_changed(self, theme_data: dict) -> None:
        color = resolve_theme_color(theme_data, Colors.ICON)
        self._close_btn.setIcon(qta.icon(QtAwesomeIcons.CLOSE, color=color))
