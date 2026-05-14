from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QLabel,
)

import qtawesome as qta

from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.flow_layout import FlowLayout
from ui.components.inline_banner import InlineBanner
from ui.components.search_bar import SearchBar


class ContentView(QFrame):
    """Orta panel: arama cubugu + FlowLayout kart alani."""

    add_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ContentView")
        self._build_ui()
        self._connect_signals()
        event_bus.theme_changed.connect(self._on_theme_changed)

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # --- Üst bar ---
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self._search_bar = SearchBar()
        top_bar.addWidget(self._search_bar, stretch=1)

        self._add_btn = QPushButton(AppStrings.ADD_NEW)
        self._add_btn.setObjectName("AddButton")
        self._add_btn.setIcon(qta.icon(QtAwesomeIcons.ADD, color="#ffffff"))
        top_bar.addWidget(self._add_btn)

        root.addLayout(top_bar)

        # --- Inline banner ---
        self._banner = InlineBanner()
        root.addWidget(self._banner)

        # --- Kart alanı ---
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setObjectName("CardScrollArea")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._card_container = QWidget()
        self._card_container.setObjectName("CardContainer")
        self._flow_layout = FlowLayout(self._card_container, h_spacing=12, v_spacing=12)
        self._card_container.setLayout(self._flow_layout)

        self._scroll.setWidget(self._card_container)
        root.addWidget(self._scroll)

        # --- Boş durum widget'ı ---
        self._empty_state = QLabel(AppStrings.EMPTY_STATE_MSG)
        self._empty_state.setObjectName("EmptyStateLabel")
        self._empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_state.setWordWrap(True)
        self._empty_state.hide()
        root.addWidget(self._empty_state)

    def _connect_signals(self) -> None:
        self._add_btn.clicked.connect(self.add_requested)
        self._search_bar.search_changed.connect(event_bus.search_query_changed)

    # ------------------------------------------------------------------ #
    # Kart yönetimi
    # ------------------------------------------------------------------ #

    def clear_cards(self) -> None:
        while self._flow_layout.count():
            item = self._flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def add_card(self, card: QWidget) -> None:
        self._flow_layout.addWidget(card)

    def show_empty_state(self, visible: bool) -> None:
        self._scroll.setVisible(not visible)
        self._empty_state.setVisible(visible)

    # ------------------------------------------------------------------ #
    # Banner API
    # ------------------------------------------------------------------ #

    def show_error_banner(self, message: str) -> None:
        self._banner.show_error(message)

    def show_info_banner(self, message: str) -> None:
        self._banner.show_info(message)

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_theme_changed(self, theme_data: dict) -> None:
        icon_color = theme_data.get("icon_color", "#ffffff")
        self._add_btn.setIcon(qta.icon(QtAwesomeIcons.ADD, color=icon_color))
