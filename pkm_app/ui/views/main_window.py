from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QSplitter,
    QWidget,
    QHBoxLayout,
)

from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.sidebar import Sidebar
from ui.views.content_view import ContentView
from ui.views.detail_view import DetailView


class MainWindow(QMainWindow):
    """Three-Pane ana pencere: Sidebar | ContentView | DetailView."""

    def __init__(self, controller) -> None:
        super().__init__()
        self._controller = controller
        self.setWindowTitle(AppStrings.APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(900, 600)

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

        # Sidebar sabit genislikte — splitter disinda
        self._sidebar = Sidebar()
        root_layout.addWidget(self._sidebar)

        # Orta ve sag panel splitter ile ayrilir
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setObjectName("MainSplitter")
        self._splitter.setChildrenCollapsible(False)

        self._content_view = ContentView()
        self._detail_view = DetailView()

        self._splitter.addWidget(self._content_view)
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
        self._content_view.add_requested.connect(self._on_add_requested)
        self._detail_view.progress_updated.connect(
            self._controller.update_progress
        )

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

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_filter_changed(self, filter_key: str) -> None:
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
        # TODO: Adim 8'de dialog eklenecek
        pass

    def _refresh_current(self, _resource_id: int = 0) -> None:
        self._load_resources(getattr(self, "_current_filter", "all"))
