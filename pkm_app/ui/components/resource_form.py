from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.constants.strings import AppStrings
from models.resource import ResourceStatus


class ResourceForm(QFrame):
    """Yeni kaynak ekleme formu — sag panelde goruntulenir, QDialog kullanilmaz."""

    submitted = Signal(dict)
    cancelled = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ResourceForm")
        self._categories: list = []
        self._build_ui()

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        header = QLabel(AppStrings.FORM_HEADER)
        header.setObjectName("FormHeader")
        root.addWidget(header)

        self._title_input = self._field(root, AppStrings.FORM_FIELD_TITLE)
        self._url_input = self._field(root, AppStrings.FORM_FIELD_URL)

        root.addWidget(QLabel(AppStrings.FORM_FIELD_CATEGORY))
        self._category_combo = QComboBox()
        self._category_combo.setObjectName("FormCombo")
        root.addWidget(self._category_combo)

        root.addWidget(QLabel(AppStrings.FORM_FIELD_PRIORITY))
        self._priority_combo = QComboBox()
        self._priority_combo.setObjectName("FormCombo")
        self._priority_combo.addItem(AppStrings.FORM_PRIORITY_MEDIUM, 2)
        self._priority_combo.addItem(AppStrings.FORM_PRIORITY_HIGH, 1)
        self._priority_combo.addItem(AppStrings.FORM_PRIORITY_LOW, 3)
        root.addWidget(self._priority_combo)

        self._tags_input = self._field(root, AppStrings.FORM_FIELD_TAGS)

        root.addWidget(QLabel(AppStrings.FORM_FIELD_CONTENT))
        self._content_input = QTextEdit()
        self._content_input.setObjectName("FormTextEdit")
        self._content_input.setMaximumHeight(100)
        root.addWidget(self._content_input)

        root.addStretch(1)

        btn_row = QHBoxLayout()
        self._save_btn = QPushButton(AppStrings.SAVE)
        self._save_btn.setObjectName("SaveButton")
        self._cancel_btn = QPushButton(AppStrings.CANCEL)
        self._cancel_btn.setObjectName("CancelButton")
        btn_row.addWidget(self._cancel_btn)
        btn_row.addWidget(self._save_btn)
        root.addLayout(btn_row)

        self._save_btn.clicked.connect(self._on_save)
        self._cancel_btn.clicked.connect(self.cancelled)

    @staticmethod
    def _field(layout: QVBoxLayout, label: str) -> QLineEdit:
        layout.addWidget(QLabel(label))
        field = QLineEdit()
        field.setObjectName("FormField")
        layout.addWidget(field)
        return field

    # ------------------------------------------------------------------ #
    # Veri
    # ------------------------------------------------------------------ #

    def load_categories(self, categories: list) -> None:
        self._categories = categories
        self._category_combo.clear()
        self._category_combo.addItem(AppStrings.FORM_CATEGORY_NONE, None)
        for cat in categories:
            self._category_combo.addItem(cat.name, cat.id)

    def reset(self) -> None:
        self._title_input.clear()
        self._url_input.clear()
        self._tags_input.clear()
        self._content_input.clear()
        self._priority_combo.setCurrentIndex(0)
        self._category_combo.setCurrentIndex(0)

    # ------------------------------------------------------------------ #
    # Slot
    # ------------------------------------------------------------------ #

    def _on_save(self) -> None:
        title = self._title_input.text().strip()
        if not title:
            from core.events import event_bus
            event_bus.error_occurred.emit(AppStrings.ERR_TITLE_REQUIRED)
            return

        url = self._url_input.text().strip() or None
        category_id = self._category_combo.currentData()
        priority = self._priority_combo.currentData()
        raw_tags = self._tags_input.text()
        tag_names = [t.strip() for t in raw_tags.split(",") if t.strip()]
        content = self._content_input.toPlainText().strip() or None

        self.submitted.emit({
            "title": title,
            "url": url,
            "category_id": category_id,
            "priority": priority,
            "status": ResourceStatus.PLANNED,
            "tag_names": tag_names,
            "content": content,
        })
