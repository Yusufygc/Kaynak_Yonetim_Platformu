from PySide6.QtCore import Signal
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from models import Resource
from ui.components.resource_card import ResourceCard
from ui.views.content_view import ContentView
from ui.views.settings_view import SettingsView
from ui.views.url_showcase_view import UrlShowcaseView

_PAGE_CONTENT = 0
_PAGE_SETTINGS = 1
_PAGE_URL_SHOWCASE = 2


class ContentWorkspace(QWidget):
    """Orta panel: ContentView / SettingsView / UrlShowcaseView arasi filter dispatcher.

    Sidebar'dan gelen filter_key'i alir, dogru sayfayi gosterir ve controller
    araciligiyla kayitlari listeler. Detay paneli ile dogrudan etkilesmez;
    karsilikli kupling olmamasi icin yalnizca ContentView'in `add_requested`
    sinyalini disariya relay eder.
    """

    add_requested = Signal()

    def __init__(self, controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._controller = controller
        self._current_filter: str = "all"

        self._build_ui()

        # Filter -> handler dispatch tablosu. apply_filter icinde kullanilir.
        self._dispatch = {
            "settings": self._show_settings,
            "url_showcase": self._show_url_showcase,
        }

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
        """Sidebar veya search'ten gelen filter_key'i uygular."""
        handler = self._dispatch.get(filter_key)
        if handler is not None:
            handler()
            return

        if filter_key.startswith("search:"):
            self._show_search(filter_key[len("search:"):])
            return

        self._show_content(filter_key)

    def refresh(self) -> None:
        """Aktif filter'i tekrar uygular (kaynak ekleme/silme/guncelleme sonrasi)."""
        idx = self._stack.currentIndex()
        if idx == _PAGE_URL_SHOWCASE:
            self._show_url_showcase()
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
        resources = self._controller.load_resources_by_filter("url_showcase")
        self._url_showcase.load_resources(resources)

    def _show_search(self, keyword: str) -> None:
        self._stack.setCurrentIndex(_PAGE_CONTENT)
        resources = self._controller.search_resources(keyword)
        self._render_resources(resources)

    def _show_content(self, filter_key: str) -> None:
        self._current_filter = filter_key
        self._stack.setCurrentIndex(_PAGE_CONTENT)
        resources = self._controller.load_resources_by_filter(filter_key)
        self._render_resources(resources)

    def _render_resources(self, resources: list[Resource]) -> None:
        self._content_view.clear_cards()
        if not resources:
            self._content_view.show_empty_state(True)
            return
        self._content_view.show_empty_state(False)
        for resource in resources:
            self._content_view.add_card(ResourceCard(resource))
