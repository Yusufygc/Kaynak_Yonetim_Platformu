from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus


_STATIC_ITEMS = [
    (AppStrings.ALL_RESOURCES, QtAwesomeIcons.ALL_RESOURCES, "all"),
    (AppStrings.INBOX, QtAwesomeIcons.INBOX, "inbox"),
    (AppStrings.PLANNED, QtAwesomeIcons.PLANNED, "planned"),
    (AppStrings.URL_SHOWCASE, QtAwesomeIcons.URL_SHOWCASE, "url_showcase"),
    (AppStrings.SETTINGS, QtAwesomeIcons.SETTINGS, "settings"),
]


class Sidebar(QFrame):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(220)

        self._theme: dict = {}
        self._build_ui()
        self._connect_signals()

        event_bus.theme_changed.connect(self._on_theme_changed)

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 16, 8, 8)
        layout.setSpacing(4)

        # Uygulama basligi
        title = QLabel(AppStrings.APP_TITLE)
        title.setObjectName("SidebarTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(12)

        # Statik navigasyon listesi
        self._nav_list = QListWidget()
        self._nav_list.setObjectName("SidebarNavList")
        self._nav_list.setSpacing(2)
        for label, icon_name, key in _STATIC_ITEMS:
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self._nav_list.addItem(item)
        layout.addWidget(self._nav_list)

        layout.addSpacing(8)

        # Kategoriler baslik
        cat_label = QLabel(AppStrings.CATEGORIES)
        cat_label.setObjectName("SidebarSectionLabel")
        layout.addWidget(cat_label)

        self._category_list = QListWidget()
        self._category_list.setObjectName("SidebarCategoryList")
        self._category_list.setSpacing(2)
        layout.addWidget(self._category_list)

        layout.addSpacing(8)

        # Etiketler baslik
        tag_label = QLabel(AppStrings.TAGS)
        tag_label.setObjectName("SidebarSectionLabel")
        layout.addWidget(tag_label)

        self._tag_list = QListWidget()
        self._tag_list.setObjectName("SidebarTagList")
        self._tag_list.setMaximumHeight(120)
        layout.addWidget(self._tag_list)

        layout.addStretch()

        # Tema degistir butonu
        self._theme_btn = QPushButton(AppStrings.TOGGLE_THEME)
        self._theme_btn.setObjectName("ThemeToggleButton")
        layout.addWidget(self._theme_btn)

    def _connect_signals(self) -> None:
        self._nav_list.currentItemChanged.connect(self._on_nav_changed)
        self._category_list.currentItemChanged.connect(self._on_category_changed)
        self._theme_btn.clicked.connect(self._on_theme_toggle)

    # ------------------------------------------------------------------ #
    # Veri yükleme
    # ------------------------------------------------------------------ #

    def load_categories(self, categories: list) -> None:
        self._category_list.clear()
        for cat in categories:
            item = QListWidgetItem(cat.name)
            item.setData(Qt.ItemDataRole.UserRole, f"category:{cat.id}")
            self._category_list.addItem(item)

    def load_tags(self, tags: list) -> None:
        self._tag_list.clear()
        for tag in tags:
            item = QListWidgetItem(f"#{tag.name}")
            item.setData(Qt.ItemDataRole.UserRole, f"tag:{tag.id}")
            self._tag_list.addItem(item)

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_nav_changed(self, current, _previous) -> None:
        if current:
            event_bus.sidebar_filter_changed.emit(
                current.data(Qt.ItemDataRole.UserRole)
            )

    def _on_category_changed(self, current, _previous) -> None:
        if current:
            self._nav_list.clearSelection()
            event_bus.sidebar_filter_changed.emit(
                current.data(Qt.ItemDataRole.UserRole)
            )

    def _on_theme_toggle(self) -> None:
        from core.theme_manager import theme_manager
        theme_manager.toggle_theme()

    def _on_theme_changed(self, theme_data: dict) -> None:
        self._theme = theme_data
        icon_color = theme_data.get("icon_color", "#ffffff")
        moon_sun = "fa5s.sun" if theme_data.get("name") == "dark" else "fa5s.moon"
        self._theme_btn.setIcon(qta.icon(moon_sun, color=icon_color))
