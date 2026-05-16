from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.constants.strings import AppStrings
from core.events import event_bus
from ui.components.category_row import CategoryRow
from ui.components.inline_banner import InlineBanner
from ui.components.tag_row import TagRow


class SettingsView(QFrame):
    """Ayarlar sayfasi: Kategoriler ve Etiketler CRUD."""

    def __init__(self, controller, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsView")
        self._controller = controller
        self._category_rows: dict[int, CategoryRow] = {}
        self._tag_rows: dict[int, TagRow] = {}

        self._build_ui()
        self._connect_events()

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QLabel(AppStrings.SETTINGS)
        header.setObjectName("SettingsHeader")
        root.addWidget(header)

        self._banner = InlineBanner()
        root.addWidget(self._banner)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("SettingsTabs")

        self._tabs.addTab(self._build_category_tab(), AppStrings.SETTINGS_CATEGORIES_TAB)
        self._tabs.addTab(self._build_tag_tab(), AppStrings.SETTINGS_TAGS_TAB)

        root.addWidget(self._tabs, stretch=1)

    def _build_category_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Scroll alani
        self._cat_scroll = QScrollArea()
        self._cat_scroll.setWidgetResizable(True)
        self._cat_scroll.setObjectName("SettingsScrollArea")

        self._cat_list_container = QWidget()
        self._cat_list_layout = QVBoxLayout(self._cat_list_container)
        self._cat_list_layout.setContentsMargins(0, 0, 0, 0)
        self._cat_list_layout.setSpacing(4)
        self._cat_list_layout.addStretch()

        self._cat_scroll.setWidget(self._cat_list_container)
        layout.addWidget(self._cat_scroll, stretch=1)

        # Yeni kategori ekleme formu
        add_row = QHBoxLayout()
        add_row.setSpacing(6)

        self._cat_name_input = QLineEdit()
        self._cat_name_input.setObjectName("FormField")
        self._cat_name_input.setPlaceholderText(AppStrings.CATEGORY_NAME)
        add_row.addWidget(self._cat_name_input, stretch=2)

        self._cat_color_input = QLineEdit()
        self._cat_color_input.setObjectName("FormField")
        self._cat_color_input.setPlaceholderText(AppStrings.CATEGORY_COLOR)
        self._cat_color_input.setFixedWidth(120)
        add_row.addWidget(self._cat_color_input)

        self._cat_icon_input = QLineEdit()
        self._cat_icon_input.setObjectName("FormField")
        self._cat_icon_input.setPlaceholderText(AppStrings.CATEGORY_ICON)
        self._cat_icon_input.setFixedWidth(120)
        add_row.addWidget(self._cat_icon_input)

        self._cat_add_btn = QPushButton(AppStrings.ADD)
        self._cat_add_btn.setObjectName("SaveButton")
        self._cat_add_btn.setFixedWidth(70)
        add_row.addWidget(self._cat_add_btn)

        layout.addLayout(add_row)

        self._cat_add_btn.clicked.connect(self._on_add_category)
        self._cat_name_input.returnPressed.connect(self._on_add_category)

        return w

    def _build_tag_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._tag_scroll = QScrollArea()
        self._tag_scroll.setWidgetResizable(True)
        self._tag_scroll.setObjectName("SettingsScrollArea")

        self._tag_list_container = QWidget()
        self._tag_list_layout = QVBoxLayout(self._tag_list_container)
        self._tag_list_layout.setContentsMargins(0, 0, 0, 0)
        self._tag_list_layout.setSpacing(4)
        self._tag_list_layout.addStretch()

        self._tag_scroll.setWidget(self._tag_list_container)
        layout.addWidget(self._tag_scroll, stretch=1)

        # Yeni etiket ekleme
        add_row = QHBoxLayout()
        add_row.setSpacing(6)

        self._tag_name_input = QLineEdit()
        self._tag_name_input.setObjectName("FormField")
        self._tag_name_input.setPlaceholderText(AppStrings.TAG_NAME)
        add_row.addWidget(self._tag_name_input, stretch=1)

        self._tag_add_btn = QPushButton(AppStrings.ADD)
        self._tag_add_btn.setObjectName("SaveButton")
        self._tag_add_btn.setFixedWidth(70)
        add_row.addWidget(self._tag_add_btn)

        layout.addLayout(add_row)

        self._tag_add_btn.clicked.connect(self._on_add_tag)
        self._tag_name_input.returnPressed.connect(self._on_add_tag)

        return w

    # ------------------------------------------------------------------ #
    # Event Bus
    # ------------------------------------------------------------------ #

    def _connect_events(self) -> None:
        event_bus.category_added.connect(self._reload_categories)
        event_bus.category_updated.connect(self._reload_categories)
        event_bus.category_deleted.connect(self._reload_categories)
        event_bus.tag_added.connect(self._reload_tags)
        event_bus.tag_updated.connect(self._reload_tags)
        event_bus.tag_deleted.connect(self._reload_tags)
        event_bus.error_occurred.connect(self._banner.show_error)

    # ------------------------------------------------------------------ #
    # Veri yukleme
    # ------------------------------------------------------------------ #

    def load_all(self) -> None:
        self._reload_categories()
        self._reload_tags()

    def _reload_categories(self, _id: int = 0) -> None:
        self._reload_rows(
            layout=self._cat_list_layout,
            rows=self._category_rows,
            items=self._controller.load_categories(),
            row_cls=CategoryRow,
            on_edit=self._on_edit_category,
            on_delete=self._on_delete_category,
        )

    def _reload_tags(self, _id: int = 0) -> None:
        self._reload_rows(
            layout=self._tag_list_layout,
            rows=self._tag_rows,
            items=self._controller.load_tags(),
            row_cls=TagRow,
            on_edit=self._on_edit_tag,
            on_delete=self._on_delete_tag,
        )

    def _reload_rows(self, *, layout: QVBoxLayout, rows: dict,
                     items: list, row_cls, on_edit, on_delete) -> None:
        self._clear_layout(layout)
        rows.clear()
        for item in items:
            row = row_cls(item)
            row.edit_requested.connect(on_edit)
            row.delete_requested.connect(on_delete)
            layout.insertWidget(layout.count() - 1, row)
            rows[item.id] = row

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count() > 1:  # son eleman stretch
            item = layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _on_add_category(self) -> None:
        name = self._cat_name_input.text().strip()
        color = self._cat_color_input.text().strip()
        icon = self._cat_icon_input.text().strip()
        if not name or not color:
            self._banner.show_error("Ad ve renk zorunludur.")
            return
        result = self._controller.create_category(name, color, icon)
        if result:
            self._cat_name_input.clear()
            self._cat_color_input.clear()
            self._cat_icon_input.clear()
            self._banner.show_info(f"'{result.name}' kategorisi eklendi.")

    def _on_edit_category(self, cat_id: int, name: str,
                          color_hex: str, icon: str) -> None:
        self._controller.update_category(cat_id, name, color_hex, icon)

    def _on_delete_category(self, cat_id: int) -> None:
        self._controller.delete_category(cat_id)

    def _on_add_tag(self) -> None:
        name = self._tag_name_input.text().strip()
        if not name:
            self._banner.show_error("Etiket adi bos olamaz.")
            return
        result = self._controller.create_tag(name)
        if result:
            self._tag_name_input.clear()
            self._banner.show_info(f"'#{result.name}' etiketi eklendi.")

    def _on_edit_tag(self, tag_id: int, new_name: str) -> None:
        self._controller.update_tag(tag_id, new_name)

    def _on_delete_tag(self, tag_id: int) -> None:
        self._controller.delete_tag(tag_id)
