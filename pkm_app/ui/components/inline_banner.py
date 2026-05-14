from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel, QWidget


class InlineBanner(QLabel):
    """Ust alana gomulu, otomatik kapanan bildirim bandi."""

    _AUTO_HIDE_MS = 3500

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("InlineBanner")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        self.hide()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.hide)

    def show_error(self, message: str) -> None:
        self._show(message, "error")

    def show_info(self, message: str) -> None:
        self._show(message, "info")

    def _show(self, message: str, severity: str) -> None:
        self._timer.stop()
        self.setText(message)
        self.setProperty("severity", severity)
        # QSS property degeri degistiginde stilin yeniden uygulanmasi gerekir
        self.style().unpolish(self)
        self.style().polish(self)
        self.show()
        self._timer.start(self._AUTO_HIDE_MS)
