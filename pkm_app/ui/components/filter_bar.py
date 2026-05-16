from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QToolButton,
    QWidget,
    QWidgetAction,
)

import qtawesome as qta

from core.constants.colors import Colors
from core.constants.icons import QtAwesomeIcons
from core.constants.status import status_label
from core.constants.strings import AppStrings
from core.events import event_bus
from models import ResourceStatus
from ui.theme_utils import resolve_theme_color


_PRIORITY_LABELS = [
    (1, AppStrings.FORM_PRIORITY_HIGH),
    (2, AppStrings.FORM_PRIORITY_MEDIUM),
    (3, AppStrings.FORM_PRIORITY_LOW),
]


class _ToggleChip(QPushButton):
    """Tek satirlik secilebilir chip."""

    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setObjectName("FilterChip")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class FilterBar(QFrame):
    """Kategori + Etiket + Durum + Oncelik kombinasyonel filtre cubugu.

    Herhangi bir kontrol degisince `filters_changed(dict)` emit eder.
    Sozluk semasi:
      {
        "category_id": int|None,
        "tag_ids": list[int],
        "statuses": list[ResourceStatus],
        "priorities": list[int],
      }
    """

    filters_changed = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("FilterBar")
        self._categories: list = []
        self._tags: list = []
        self._status_chips: dict[ResourceStatus, _ToggleChip] = {}
        self._priority_chips: dict[int, _ToggleChip] = {}
        self._suppress_emit = False

        self._build_ui()
        event_bus.theme_changed.connect(self._on_theme_changed)

    # ------------------------------------------------------------------ #
    # Kurulum
    # ------------------------------------------------------------------ #

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # --- Kategori dropdown ---
        layout.addWidget(self._label(AppStrings.FILTER_CATEGORY))
        self._category_combo = QComboBox()
        self._category_combo.setObjectName("FilterCombo")
        self._category_combo.addItem(AppStrings.FILTER_ANY, None)
        self._category_combo.currentIndexChanged.connect(self._emit_filters)
        layout.addWidget(self._category_combo)

        # --- Etiket multi-select dropdown ---
        layout.addWidget(self._label(AppStrings.FILTER_TAG))
        self._tag_button = QToolButton()
        self._tag_button.setObjectName("FilterTagButton")
        self._tag_button.setText(AppStrings.FILTER_TAG_PLACEHOLDER)
        self._tag_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._tag_menu = QMenu(self._tag_button)
        self._tag_list = QListWidget()
        self._tag_list.setObjectName("FilterTagList")
        self._tag_list.setMinimumWidth(180)
        self._tag_list.setMaximumHeight(220)
        self._tag_list.itemChanged.connect(self._on_tag_item_changed)
        tag_action = QWidgetAction(self._tag_menu)
        tag_action.setDefaultWidget(self._tag_list)
        self._tag_menu.addAction(tag_action)
        self._tag_button.setMenu(self._tag_menu)
        layout.addWidget(self._tag_button)

        # --- Durum chip'leri ---
        layout.addWidget(self._label(AppStrings.FILTER_STATUS))
        for status in ResourceStatus:
            chip = _ToggleChip(status_label(status))
            chip.toggled.connect(self._emit_filters)
            self._status_chips[status] = chip
            layout.addWidget(chip)

        # --- Oncelik chip'leri ---
        layout.addWidget(self._label(AppStrings.FILTER_PRIORITY))
        for value, label in _PRIORITY_LABELS:
            chip = _ToggleChip(label)
            chip.toggled.connect(self._emit_filters)
            self._priority_chips[value] = chip
            layout.addWidget(chip)

        layout.addStretch(1)

        # --- Temizle ---
        self._clear_btn = QToolButton()
        self._clear_btn.setObjectName("FilterClearButton")
        self._clear_btn.setText(AppStrings.FILTER_CLEAR)
        self._clear_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._refresh_clear_icon()
        self._clear_btn.clicked.connect(self.clear)
        layout.addWidget(self._clear_btn)

    @staticmethod
    def _label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("FilterLabel")
        return lbl

    def _refresh_clear_icon(self) -> None:
        color = resolve_theme_color(None, Colors.ICON)
        self._clear_btn.setIcon(qta.icon(QtAwesomeIcons.FILTER_CLEAR, color=color))

    def _on_theme_changed(self, theme_data: dict) -> None:
        color = resolve_theme_color(theme_data, Colors.ICON)
        self._clear_btn.setIcon(qta.icon(QtAwesomeIcons.FILTER_CLEAR, color=color))

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def set_categories(self, categories: list) -> None:
        self._categories = list(categories)
        self._suppress_emit = True
        current = self._category_combo.currentData()
        self._category_combo.clear()
        self._category_combo.addItem(AppStrings.FILTER_ANY, None)
        for cat in self._categories:
            self._category_combo.addItem(cat.name, cat.id)
        idx = self._category_combo.findData(current)
        self._category_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self._suppress_emit = False

    def set_tags(self, tags: list) -> None:
        self._tags = list(tags)
        current_ids = set(self._selected_tag_ids())
        self._suppress_emit = True
        self._tag_list.clear()
        for tag in self._tags:
            item = QListWidgetItem(f"#{tag.name}")
            item.setData(Qt.ItemDataRole.UserRole, tag.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                Qt.CheckState.Checked if tag.id in current_ids else Qt.CheckState.Unchecked
            )
            self._tag_list.addItem(item)
        self._suppress_emit = False
        self._refresh_tag_button_text()

    def current_filters(self) -> dict:
        return {
            "category_id": self._category_combo.currentData(),
            "tag_ids": self._selected_tag_ids(),
            "statuses": [s for s, chip in self._status_chips.items() if chip.isChecked()],
            "priorities": [p for p, chip in self._priority_chips.items() if chip.isChecked()],
        }

    def clear(self) -> None:
        self._suppress_emit = True
        self._category_combo.setCurrentIndex(0)
        for i in range(self._tag_list.count()):
            self._tag_list.item(i).setCheckState(Qt.CheckState.Unchecked)
        for chip in self._status_chips.values():
            chip.setChecked(False)
        for chip in self._priority_chips.values():
            chip.setChecked(False)
        self._suppress_emit = False
        self._refresh_tag_button_text()
        self._emit_filters()

    # ------------------------------------------------------------------ #
    # Slot'lar
    # ------------------------------------------------------------------ #

    def _selected_tag_ids(self) -> list[int]:
        return [
            self._tag_list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._tag_list.count())
            if self._tag_list.item(i).checkState() == Qt.CheckState.Checked
        ]

    def _on_tag_item_changed(self, _item: QListWidgetItem) -> None:
        self._refresh_tag_button_text()
        self._emit_filters()

    def _refresh_tag_button_text(self) -> None:
        ids = self._selected_tag_ids()
        if not ids:
            self._tag_button.setText(AppStrings.FILTER_TAG_PLACEHOLDER)
        else:
            self._tag_button.setText(f"{AppStrings.FILTER_TAG} ({len(ids)})")

    def _emit_filters(self, *_args) -> None:
        if self._suppress_emit:
            return
        self.filters_changed.emit(self.current_filters())
