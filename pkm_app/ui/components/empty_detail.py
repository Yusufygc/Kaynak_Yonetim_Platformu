from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EmptyDetail(QWidget):
    """Detay paneli bos durumu."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("Bir kaynak seçin\nveya 'Yeni Ekle'ye basın.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setObjectName("EmptyDetailLabel")
        layout.addWidget(label)
