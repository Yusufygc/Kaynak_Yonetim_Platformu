from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLineEdit

from core.constants.strings import AppStrings


class SearchBar(QLineEdit):
    """Arama cubugu — metin degisince event_bus'a sinyal gonder."""

    search_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setPlaceholderText(AppStrings.SEARCH_PLACEHOLDER)
        self.setObjectName("SearchBar")
        self.textChanged.connect(self.search_changed)
