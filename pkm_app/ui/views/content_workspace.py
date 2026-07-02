from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from core.events import event_bus
from models import Resource, ResourceStatus
from ui.components.resource_card import ResourceCard
from ui.views.content_view import ContentView
from ui.views.settings_view import SettingsView
from ui.views.url_showcase_view import UrlShowcaseView

_PAGE_CONTENT = 0
_PAGE_SETTINGS = 1
_PAGE_URL_SHOWCASE = 2


class ContentWorkspace(QWidget):
    """Orta panel: ContentView / SettingsView / UrlShowcaseView arasi filter dispatcher.

    Sidebar'dan gelen filter_key'i (all/inbox/planned/favorites/url_showcase/settings)
    ve FilterBar'dan gelen kombinasyonel filtreleri birlestirip controller'a iletir.
    Aktif sayfa + aktif filtre kombinasyonu state olarak burada tutulur.
    """

    add_requested = Signal()

    def __init__(self, controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._current_filter: str = "all"
        self._active_filters: dict = {}

        self._build_ui()

        self._dispatch = {
            "settings": self._show_settings,
            "url_showcase": self._show_url_showcase,
            "favorites": self._show_favorites,
        }

        # FilterBar sinyalleri
        self._content_view.filters_changed.connect(self._on_filters_changed)
        self._url_showcase.filters_changed.connect(self._on_filters_changed)

        # Kategori/etiket CRUD sonrasi FilterBar'lari yenile
        event_bus.category_added.connect(self._refresh_filter_data)
        event_bus.category_updated.connect(self._refresh_filter_data)
        event_bus.category_deleted.connect(self._refresh_filter_data)
        event_bus.tag_added.connect(self._refresh_filter_data)
        event_bus.tag_updated.connect(self._refresh_filter_data)
        event_bus.tag_deleted.connect(self._refresh_filter_data)

        self._refresh_filter_data()

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._stack = QStackedWidget()
        self._content_view = ContentView()
        self._settings_view = SettingsView(self._controller)
        self._url_showcase = UrlShowcaseView()

        self._stack.addWidget(self._content_view)    # _PAGE_CONTENT
        self._stack.addWidget(self._settings_view)   # _PAGE_SETTINGS
        self._stack.addWidget(self._url_showcase)    # _PAGE_URL_SHOWCASE

        root.addWidget(self._stack)

        self._content_view.add_requested.connect(self.add_requested)

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def apply_filter(self, filter_key: str) -> None:
        # Sidebar geçişi yeni bağlam → FilterBar resetle.
        self._active_filters = {}
        self._content_view.filter_bar.clear()
        self._url_showcase.filter_bar.clear()

        handler = self._dispatch.get(filter_key)
        if handler is not None:
            handler()
            return

        if filter_key.startswith("search:"):
            self._show_search(filter_key[len("search:"):])
            return

        self._show_content(filter_key)

    def refresh(self) -> None:
        idx = self._stack.currentIndex()
        if idx == _PAGE_URL_SHOWCASE:
            self._show_url_showcase()
        elif idx == _PAGE_SETTINGS:
            self._show_settings()
        elif self._current_filter == "favorites":
            self._show_favorites()
        else:
            self._show_content(self._current_filter)

    def show_info_banner(self, message: str) -> None:
        self._content_view.show_info_banner(message)

    def show_error_banner(self, message: str) -> None:
        self._content_view.show_error_banner(message)

    def is_content_active(self) -> bool:
        return self._stack.currentIndex() == _PAGE_CONTENT

    # ------------------------------------------------------------------ #
    # Sayfa gostericiler
    # ------------------------------------------------------------------ #

    def _show_settings(self) -> None:
        self._stack.setCurrentIndex(_PAGE_SETTINGS)
        self._settings_view.load_all()

    def _show_url_showcase(self) -> None:
        self._stack.setCurrentIndex(_PAGE_URL_SHOWCASE)
        filters = {**self._active_filters, "urls_only": True}
        resources = self._controller.load_resources_with_filters(filters)
        self._url_showcase.load_resources(resources)

    def _show_favorites(self) -> None:
        self._current_filter = "favorites"
        self._stack.setCurrentIndex(_PAGE_CONTENT)
        filters = {**self._active_filters, "favorites_only": True}
        resources = self._controller.load_resources_with_filters(filters)
        self._render_resources(resources)

    def _show_search(self, keyword: str) -> None:
        self._stack.setCurrentIndex(_PAGE_CONTENT)
        filters = {**self._active_filters, "keyword": keyword}
        resources = self._controller.load_resources_with_filters(filters)
        self._render_resources(resources)

    def _show_content(self, filter_key: str) -> None:
        self._current_filter = filter_key
        self._stack.setCurrentIndex(_PAGE_CONTENT)
        filters = self._merged_filters_for_sidebar(filter_key)
        resources = self._controller.load_resources_with_filters(filters)
        self._render_resources(resources)

    def _merged_filters_for_sidebar(self, filter_key: str) -> dict:
        filters = {**self._active_filters}
        if filter_key == "inbox":
            filters["statuses"] = [ResourceStatus.INBOX]
        elif filter_key == "planned":
            filters["statuses"] = [ResourceStatus.PLANNED]
        elif filter_key.startswith("category:"):
            filters["category_id"] = int(filter_key.split(":")[1])
        # "all" → ek koşul yok
        return filters

    def _render_resources(self, resources: list[Resource]) -> None:
        self._content_view.clear_cards()
        if not resources:
            self._content_view.show_empty_state(True)
            return
        self._content_view.show_empty_state(False)
        for resource in resources:
            self._content_view.add_card(ResourceCard(resource))

    # ------------------------------------------------------------------ #
    # FilterBar slot'lari
    # ------------------------------------------------------------------ #

    def _on_filters_changed(self, filters: dict) -> None:
        self._active_filters = filters
        self.refresh()

    def _refresh_filter_data(self, *_args) -> None:
        categories = self._controller.load_categories()
        tags = self._controller.load_tags()
        for fb in (self._content_view.filter_bar, self._url_showcase.filter_bar):
            fb.set_categories(categories)
            fb.set_tags(tags)
