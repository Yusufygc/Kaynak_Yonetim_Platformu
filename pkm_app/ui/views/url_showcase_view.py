from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
)

import qtawesome as qta

from core.constants.colors import Colors
from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.filter_bar import FilterBar
from ui.components.flow_layout import build_flow_stack, clear_flow, EMPTY_PAGE, GRID_PAGE
from ui.components.inline_banner import InlineBanner
from ui.components.search_bar import SearchBar
from ui.theme_utils import resolve_theme_color

_RICH_MODE = 0
_SIMPLE_MODE = 1


class UrlShowcaseView(QFrame):
    """'Baglanti Vitrini' sekmesi — ana sayfa.

    Iki gorunum modu tasir:
    - rich (varsayilan): sadece URL'li kaynaklar, buyuk gorsel UrlRichCard'lar.
    - simple ("Sade Mod" acik): tum kaynaklar (URL kisiti yok), duz ResourceCard izgarasi
      — eskiden ayri bir "Tum Kaynaklar" sayfasinin gosterdigi gorunum.
    """

    add_requested = Signal()
    filters_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("UrlShowcaseView")
        self._simple_mode = False
        self._rich_cards: list = []
        self._simple_cards: list = []
        self._build_ui()
        self._add_btn.clicked.connect(self.add_requested)
        self.search_bar.search_changed.connect(self._emit_combined_filters)
        self.filter_bar.filters_changed.connect(self._emit_combined_filters)
        event_bus.theme_changed.connect(self._on_theme_changed)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.search_bar = SearchBar()
        top_bar.addWidget(self.search_bar, stretch=1)

        self._add_btn = QPushButton(AppStrings.ADD_NEW)
        self._add_btn.setObjectName("AddButton")
        self._add_btn.setIcon(
            qta.icon(QtAwesomeIcons.ADD, color=resolve_theme_color(None, Colors.ICON))
        )
        top_bar.addWidget(self._add_btn)

        root.addLayout(top_bar)

        self.filter_bar = FilterBar()
        root.addWidget(self.filter_bar)

        self._banner = InlineBanner()
        root.addWidget(self._banner)

        self._mode_stack = QStackedWidget()

        self._rich_stack, self._rich_flow = build_flow_stack(
            AppStrings.EMPTY_STATE_MSG,
            h_spacing=16, v_spacing=16,
            container_name="ShowcaseContainer", scroll_name="ShowcaseScrollArea",
        )
        self._mode_stack.addWidget(self._rich_stack)  # _RICH_MODE

        self._simple_stack, self._simple_flow = build_flow_stack(
            AppStrings.EMPTY_STATE_MSG,
            h_spacing=12, v_spacing=12,
            container_name="CardContainer", scroll_name="CardScrollArea",
        )
        self._mode_stack.addWidget(self._simple_stack)  # _SIMPLE_MODE

        root.addWidget(self._mode_stack, stretch=1)

    def _emit_combined_filters(self, *_args) -> None:
        filters = self.filter_bar.current_filters()
        filters["keyword"] = self.search_bar.text().strip()
        self.filters_changed.emit(filters)

    def _on_theme_changed(self, theme_data: dict) -> None:
        icon_color = resolve_theme_color(theme_data, Colors.ICON)
        self._add_btn.setIcon(qta.icon(QtAwesomeIcons.ADD, color=icon_color))

    def show_info_banner(self, message: str) -> None:
        self._banner.show_info(message)

    def show_error_banner(self, message: str) -> None:
        self._banner.show_error(message)

    def set_simple_mode(self, enabled: bool) -> None:
        self._simple_mode = enabled
        self._mode_stack.setCurrentIndex(_SIMPLE_MODE if enabled else _RICH_MODE)

    def load_resources(self, resources: list) -> None:
        if self._simple_mode:
            self._load_simple(resources)
        else:
            self._load_rich(resources)

    def _load_rich(self, resources: list) -> None:
        from ui.components.url_rich_card import UrlRichCard

        self._rich_cards.clear()
        clear_flow(self._rich_flow)

        url_resources = [r for r in resources if r.url]
        if not url_resources:
            self._rich_stack.setCurrentIndex(EMPTY_PAGE)
            return

        self._rich_stack.setCurrentIndex(GRID_PAGE)
        for resource in url_resources:
            card = UrlRichCard(resource)
            self._rich_cards.append(card)
            self._rich_flow.addWidget(card)
        self._rich_flow.parentWidget().update()

    def _load_simple(self, resources: list) -> None:
        from ui.components.resource_card import ResourceCard

        self._simple_cards.clear()
        clear_flow(self._simple_flow)

        if not resources:
            self._simple_stack.setCurrentIndex(EMPTY_PAGE)
            return

        self._simple_stack.setCurrentIndex(GRID_PAGE)
        for resource in resources:
            card = ResourceCard(resource)
            self._simple_cards.append(card)
            self._simple_flow.addWidget(card)
        self._simple_flow.parentWidget().update()
