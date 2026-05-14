from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.flow_layout import FlowLayout


class UrlShowcaseView(QFrame):
    """'Baglanti Vitrini' sekmesi — sadece URL'li kaynaklar, UrlRichCard ile."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("UrlShowcaseView")
        self._build_ui()
        event_bus.sidebar_filter_changed.connect(self._on_filter_changed)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setObjectName("ShowcaseScrollArea")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setObjectName("ShowcaseContainer")
        self._flow = FlowLayout(self._container, h_spacing=16, v_spacing=16)
        self._container.setLayout(self._flow)
        self._scroll.setWidget(self._container)
        root.addWidget(self._scroll)

        self._empty_label = QLabel(AppStrings.EMPTY_STATE_MSG)
        self._empty_label.setObjectName("EmptyStateLabel")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._empty_label.hide()
        root.addWidget(self._empty_label)

    def load_resources(self, resources: list) -> None:
        from ui.components.url_rich_card import UrlRichCard

        while self._flow.count():
            item = self._flow.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        url_resources = [r for r in resources if r.url]
        if not url_resources:
            self._scroll.hide()
            self._empty_label.show()
            return

        self._scroll.show()
        self._empty_label.hide()
        for resource in url_resources:
            self._flow.addWidget(UrlRichCard(resource))

    def _on_filter_changed(self, filter_key: str) -> None:
        # Sadece url_showcase filtresi secildiginde bu view guncellenir;
        # guncelleme MainWindow tarafından tetiklenir.
        pass
