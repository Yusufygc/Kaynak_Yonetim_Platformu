from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QWidget,
    QHBoxLayout,
)

from core.constants.strings import AppStrings
from core.events import event_bus
from core.logger import log
from ui.components.sidebar import Sidebar
from ui.views.content_view import ContentView
from ui.views.detail_view import DetailView
from ui.views.settings_view import SettingsView
from ui.views.url_showcase_view import UrlShowcaseView

_PAGE_CONTENT = 0
_PAGE_SETTINGS = 1
_PAGE_URL_SHOWCASE = 2


class MainWindow(QMainWindow):
    """Three-Pane ana pencere: Sidebar | main_stack | DetailView."""

    def __init__(self, controller) -> None:
        super().__init__()
        self._controller = controller
        self.setWindowTitle(AppStrings.APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)
        self._current_filter = "all"

        self._build_ui()
        self._connect_events()
        self._initial_load()

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._sidebar = Sidebar()
        root_layout.addWidget(self._sidebar)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setObjectName("MainSplitter")
        self._splitter.setChildrenCollapsible(False)

        self._main_stack = QStackedWidget()
        self._content_view = ContentView()
        self._settings_view = SettingsView(self._controller)
        self._url_showcase = UrlShowcaseView()
        self._main_stack.addWidget(self._content_view)    # 0
        self._main_stack.addWidget(self._settings_view)   # 1
        self._main_stack.addWidget(self._url_showcase)    # 2

        self._detail_view = DetailView()

        self._splitter.addWidget(self._main_stack)
        self._splitter.addWidget(self._detail_view)
        self._splitter.setStretchFactor(0, 3)
        self._splitter.setStretchFactor(1, 1)

        root_layout.addWidget(self._splitter, stretch=1)

    def _connect_events(self) -> None:
        event_bus.sidebar_filter_changed.connect(self._on_filter_changed)
        event_bus.resource_selected.connect(self._on_resource_selected)
        event_bus.resource_added.connect(self._refresh_current)
        event_bus.resource_updated.connect(self._refresh_current)
        event_bus.resource_deleted.connect(self._on_resource_deleted)
        event_bus.error_occurred.connect(self._on_error)

        self._content_view.add_requested.connect(self._on_add_requested)
        self._detail_view.progress_updated.connect(self._controller.update_progress)
        self._detail_view.status_updated.connect(self._on_status_updated)
        self._detail_view.content_updated.connect(self._on_content_updated)
        self._detail_view.form_submitted.connect(self._on_form_submitted)
        self._detail_view.edit_requested.connect(self._on_edit_requested)
        self._detail_view.delete_requested.connect(self._on_delete_requested)

    # ------------------------------------------------------------------ #
    # Yükleme
    # ------------------------------------------------------------------ #

    def _initial_load(self) -> None:
        self._load_resources("all")

    def _load_resources(self, filter_key: str) -> None:
        from ui.components.resource_card import ResourceCard

        self._current_filter = filter_key
        resources = self._controller.load_resources_by_filter(filter_key)

        self._content_view.clear_cards()

        if not resources:
            self._content_view.show_empty_state(True)
            return

        self._content_view.show_empty_state(False)
        for resource in resources:
            card = ResourceCard(resource)
            self._content_view.add_card(card)

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_filter_changed(self, filter_key: str) -> None:
        if filter_key == "settings":
            self._main_stack.setCurrentIndex(_PAGE_SETTINGS)
            self._detail_view.clear()
            self._settings_view.load_all()
            return

        if filter_key == "url_showcase":
            self._main_stack.setCurrentIndex(_PAGE_URL_SHOWCASE)
            resources = self._controller.load_resources_by_filter("url_showcase")
            self._url_showcase.load_resources(resources)
            return

        self._main_stack.setCurrentIndex(_PAGE_CONTENT)

        if filter_key.startswith("search:"):
            keyword = filter_key[len("search:"):]
            resources = self._controller.search_resources(keyword)
            self._content_view.clear_cards()
            if not resources:
                self._content_view.show_empty_state(True)
                return
            self._content_view.show_empty_state(False)
            from ui.components.resource_card import ResourceCard
            for r in resources:
                self._content_view.add_card(ResourceCard(r))
        else:
            self._load_resources(filter_key)

    def _on_resource_selected(self, resource_id: int) -> None:
        resource = self._controller.get_resource(resource_id)
        if resource:
            self._detail_view.load_resource(resource)

    def _on_add_requested(self) -> None:
        categories = self._controller.load_categories()
        self._detail_view.show_form(categories)

    def _on_edit_requested(self, resource_id: int) -> None:
        resource = self._controller.get_resource(resource_id)
        categories = self._controller.load_categories()
        if resource:
            self._detail_view.show_form_edit(resource, categories)

    def _on_delete_requested(self, resource_id: int) -> None:
        self._controller.delete_resource(resource_id)
        self._detail_view.clear()

    def _on_status_updated(self, resource_id: int, status) -> None:
        self._controller.update_resource(resource_id, {"status": status})

    def _on_content_updated(self, resource_id: int, text: str) -> None:
        self._controller.update_resource(resource_id, {"content": text or None})
        self._content_view.show_info_banner("Not kaydedildi.")

    def _on_form_submitted(self, data: dict) -> None:
        resource_id = data.pop("resource_id", None)
        if resource_id is None:
            resource = self._controller.add_resource(data)
            if resource is not None:
                self._detail_view.clear()
                self._load_resources(self._current_filter)
                self._content_view.show_info_banner(f"'{resource.title}' eklendi.")
                log.info("Form ile kaynak eklendi: id=%d", resource.id)
        else:
            resource = self._controller.update_resource(resource_id, data)
            if resource is not None:
                self._detail_view.load_resource(resource)
                self._load_resources(self._current_filter)
                self._content_view.show_info_banner(f"'{resource.title}' guncellendi.")
                log.info("Form ile kaynak guncellendi: id=%d", resource.id)

    def _on_error(self, message: str) -> None:
        self._content_view.show_error_banner(message)

    def _on_resource_deleted(self, _resource_id: int = 0) -> None:
        if self._main_stack.currentIndex() == _PAGE_CONTENT:
            self._load_resources(self._current_filter)

    def _refresh_current(self, _resource_id: int = 0) -> None:
        if self._main_stack.currentIndex() == _PAGE_CONTENT:
            self._load_resources(self._current_filter)
        elif self._main_stack.currentIndex() == _PAGE_URL_SHOWCASE:
            resources = self._controller.load_resources_by_filter("url_showcase")
            self._url_showcase.load_resources(resources)

        current_detail_id = self._detail_view.current_resource_id()
        if current_detail_id is not None:
            resource = self._controller.get_resource(current_detail_id)
            if resource is not None:
                self._detail_view.load_resource(resource)
