from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from core.constants.status import PRIORITY_LABELS
from core.constants.strings import AppStrings

class IdeaForm(QFrame):
    """Yeni Fikir ekleme veya duzenleme formu."""

    submitted = Signal(dict)
    cancelled = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("IdeaForm")
        self._idea_id: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Fikir Ekle/Düzenle")
        header.setObjectName("DetailTitle")
        layout.addWidget(header)

        # Title
        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("Fikrinizin kısa başlığı...")
        layout.addWidget(QLabel("Başlık:"))
        layout.addWidget(self._title_edit)

        # Priority
        self._priority_combo = QComboBox()
        for value, label in PRIORITY_LABELS.items():
            self._priority_combo.addItem(label, value)
        self._priority_combo.setCurrentIndex(1)  # Default: Orta
        layout.addWidget(QLabel("Öncelik:"))
        layout.addWidget(self._priority_combo)

        # Description
        self._desc_edit = QTextEdit()
        self._desc_edit.setPlaceholderText("Fikrinizin detayları, notlarınız...")
        layout.addWidget(QLabel("Açıklama:"))
        layout.addWidget(self._desc_edit)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        self._cancel_btn = QPushButton("İptal")
        self._cancel_btn.setObjectName("SecondaryButton")
        self._submit_btn = QPushButton("Kaydet")
        self._submit_btn.setObjectName("PrimaryButton")

        btn_layout.addStretch()
        btn_layout.addWidget(self._cancel_btn)
        btn_layout.addWidget(self._submit_btn)
        layout.addLayout(btn_layout)

        self._cancel_btn.clicked.connect(self.cancelled.emit)
        self._submit_btn.clicked.connect(self._on_submit)

    def load_idea(self, idea) -> None:
        """Formu mevcut bir Idea verisiyle doldurur."""
        self._idea_id = idea.id
        self._title_edit.setText(idea.title)
        self._desc_edit.setText(idea.description or "")
        
        # Priority combobox'i guncelle
        idx = self._priority_combo.findData(idea.priority)
        if idx >= 0:
            self._priority_combo.setCurrentIndex(idx)

    def clear(self) -> None:
        self._idea_id = None
        self._title_edit.clear()
        self._desc_edit.clear()
        self._priority_combo.setCurrentIndex(1)

    def _on_submit(self) -> None:
        title = self._title_edit.text().strip()
        if not title:
            return  # Yada bir banner gosterilebilir

        data = {
            "title": title,
            "description": self._desc_edit.toPlainText().strip(),
            "priority": self._priority_combo.currentData(),
        }
        if self._idea_id is not None:
            data["idea_id"] = self._idea_id

        self.submitted.emit(data)
