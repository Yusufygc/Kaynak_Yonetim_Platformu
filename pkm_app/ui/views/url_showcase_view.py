from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
)

from core.constants.strings import AppStrings
from ui.components.filter_bar import FilterBar
from ui.components.flow_layout import FlowLayout


class UrlShowcaseView(QFrame):
    """'Baglanti Vitrini' sekmesi — sadece URL'li kaynaklar, UrlRichCard ile."""

    filters_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("UrlShowcaseView")
        self._cards: list = []
        self._build_ui()
        self.filter_bar.filters_changed.connect(self.filters_changed)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self.filter_bar = FilterBar()
        root.addWidget(self.filter_bar)

        self._content_stack = QStackedWidget()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setObjectName("ShowcaseScrollArea")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setObjectName("ShowcaseContainer")
        self._flow = FlowLayout(self._container, h_spacing=16, v_spacing=16)
        self._container.setLayout(self._flow)
        self._scroll.setWidget(self._container)
        self._content_stack.addWidget(self._scroll)

        self._empty_label = QLabel(AppStrings.EMPTY_STATE_MSG)
        self._empty_label.setObjectName("EmptyStateLabel")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._content_stack.addWidget(self._empty_label)

        root.addWidget(self._content_stack, stretch=1)

    def load_resources(self, resources: list) -> None:
        from ui.components.url_rich_card import UrlRichCard

        # Eski kart referanslarını temizle ve sil
        self._cards.clear()
        while self._flow.count():
            item = self._flow.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        url_resources = [r for r in resources if r.url]
        if not url_resources:
            self._content_stack.setCurrentIndex(1)
            return

        self._content_stack.setCurrentIndex(0)
        for resource in url_resources:
            card = UrlRichCard(resource)
            self._cards.append(card)
            self._flow.addWidget(card)
