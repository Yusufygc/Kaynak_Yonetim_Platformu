from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QLabel,
    QStackedWidget,
)

# pyrefly: ignore [missing-import]
import qtawesome as qta

from core.constants.colors import Colors
from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.filter_bar import FilterBar
from ui.components.flow_layout import FlowLayout
from ui.components.inline_banner import InlineBanner
from ui.components.search_bar import SearchBar
from ui.theme_utils import resolve_theme_color


class ContentView(QFrame):
    """Orta panel: arama cubugu + FlowLayout kart alani."""

    add_requested = Signal()
    filters_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ContentView")
        self._cards: list = []
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
        self._add_btn.setIcon(
            qta.icon(QtAwesomeIcons.ADD, color=resolve_theme_color(None, Colors.ICON))
        )
        top_bar.addWidget(self._add_btn)

        root.addLayout(top_bar)

        # --- Filter bar ---
        self.filter_bar = FilterBar()
        root.addWidget(self.filter_bar)

        # --- Inline banner ---
        self._banner = InlineBanner()
        root.addWidget(self._banner)

        # --- Kart alanı ---
        self._content_stack = QStackedWidget()

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setObjectName("CardScrollArea")
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._card_container = QWidget()
        self._card_container.setObjectName("CardContainer")
        self._flow_layout = FlowLayout(self._card_container, h_spacing=12, v_spacing=12)
        self._card_container.setLayout(self._flow_layout)

        self._scroll.setWidget(self._card_container)
        self._content_stack.addWidget(self._scroll)

        # --- Boş durum widget'ı ---
        self._empty_state = QLabel(AppStrings.EMPTY_STATE_MSG)
        self._empty_state.setObjectName("EmptyStateLabel")
        self._empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_state.setWordWrap(True)
        self._content_stack.addWidget(self._empty_state)
        
        root.addWidget(self._content_stack, stretch=1)

    def _connect_signals(self) -> None:
        self._add_btn.clicked.connect(self.add_requested)
        self._search_bar.search_changed.connect(self._emit_combined_filters)
        self.filter_bar.filters_changed.connect(self._emit_combined_filters)

    def _emit_combined_filters(self, *_args) -> None:
        filters = self.filter_bar.current_filters()
        filters["keyword"] = self._search_bar.text().strip()
        self.filters_changed.emit(filters)

    # ------------------------------------------------------------------ #
    # Kart yönetimi
    # ------------------------------------------------------------------ #

    def clear_cards(self) -> None:
        self._cards.clear()
        while self._flow_layout.count():
            item = self._flow_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def add_card(self, card: QWidget) -> None:
        self._cards.append(card)
        self._flow_layout.addWidget(card)

    def show_empty_state(self, visible: bool) -> None:
        self._content_stack.setCurrentIndex(1 if visible else 0)

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
        icon_color = resolve_theme_color(theme_data, Colors.ICON)
        self._add_btn.setIcon(qta.icon(QtAwesomeIcons.ADD, color=icon_color))
