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

_PAGE_CONTENT = 0
_PAGE_SETTINGS = 1


class MainWindow(QMainWindow):
    """Three-Pane ana pencere: Sidebar | main_stack (ContentView/SettingsView) | DetailView."""

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

        # Ana icerik stack (ContentView | SettingsView)
        self._main_stack = QStackedWidget()
        self._content_view = ContentView()
        self._settings_view = SettingsView(self._controller)
        self._main_stack.addWidget(self._content_view)   # 0
        self._main_stack.addWidget(self._settings_view)  # 1

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
        event_bus.resource_deleted.connect(self._refresh_current)
        event_bus.error_occurred.connect(self._on_error)
        event_bus.category_added.connect(self._reload_sidebar)
        event_bus.category_updated.connect(self._reload_sidebar)
        event_bus.category_deleted.connect(self._reload_sidebar)
        event_bus.tag_added.connect(self._reload_sidebar)
        event_bus.tag_updated.connect(self._reload_sidebar)
        event_bus.tag_deleted.connect(self._reload_sidebar)

        self._content_view.add_requested.connect(self._on_add_requested)
        self._detail_view.progress_updated.connect(self._controller.update_progress)
        self._detail_view.form_submitted.connect(self._on_form_submitted)

    # ------------------------------------------------------------------ #
    # Yükleme
    # ------------------------------------------------------------------ #

    def _initial_load(self) -> None:
        categories = self._controller.load_categories()
        tags = self._controller.load_tags()
        self._sidebar.load_categories(categories)
        self._sidebar.load_tags(tags)
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

    def _reload_sidebar(self, _id: int = 0) -> None:
        self._sidebar.load_categories(self._controller.load_categories())
        self._sidebar.load_tags(self._controller.load_tags())

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_filter_changed(self, filter_key: str) -> None:
        if filter_key == "settings":
            self._main_stack.setCurrentIndex(_PAGE_SETTINGS)
            self._detail_view.clear()
            self._settings_view.load_all()
            return

        # Diger filtreler icin ContentView'e don
        self._main_stack.setCurrentIndex(_PAGE_CONTENT)

        if filter_key.startswith("search:"):
            keyword = filter_key[len("search:"):]
            resources = (
                self._controller.load_all_resources()
                if not keyword.strip()
                else self._controller._resource_svc.search(keyword)
            )
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

    def _on_form_submitted(self, data: dict) -> None:
        resource = self._controller.add_resource(data)
        if resource is not None:
            self._detail_view.clear()
            self._load_resources(self._current_filter)
            self._content_view.show_info_banner(f"'{resource.title}' eklendi.")
            log.info("Form ile kaynak eklendi: id=%d", resource.id)

    def _on_error(self, message: str) -> None:
        self._content_view.show_error_banner(message)

    def _refresh_current(self, _resource_id: int = 0) -> None:
        if self._main_stack.currentIndex() == _PAGE_CONTENT:
            self._load_resources(self._current_filter)
