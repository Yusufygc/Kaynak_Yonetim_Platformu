from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QWidget

import qtawesome as qta

from core.events import event_bus
from ui.theme_utils import resolve_theme_color


class IconActionButton(QPushButton):
    """Sade kategori/etiket satirlari icin sabit ikonlu, tema-duyarli aksiyon butonu."""

    _ICON_SIZE = 14
    _BUTTON_SIZE = 26

    def __init__(
        self,
        icon_name: str,
        color_role: str,
        tooltip: str,
        object_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._icon_name = icon_name
        self._color_role = color_role
        self._theme_data: dict | None = None

        self.setObjectName(object_name)
        self.setFixedSize(self._BUTTON_SIZE, self._BUTTON_SIZE)
        self.setIconSize(QSize(self._ICON_SIZE, self._ICON_SIZE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFlat(True)
        self.setToolTip(tooltip)

        self._refresh_icon()
        event_bus.theme_changed.connect(self._on_theme_changed)

    def set_state(self, icon_name: str, color_role: str, tooltip: str, object_name: str) -> None:
        """Ikon/renk/tooltip/objectName'i degistirir (orn. sil onay durumu)."""
        self._icon_name = icon_name
        self._color_role = color_role
        self.setToolTip(tooltip)
        self.setObjectName(object_name)
        self.style().unpolish(self)
        self.style().polish(self)
        self._refresh_icon()

    def _on_theme_changed(self, theme_data: dict) -> None:
        self._theme_data = theme_data
        self._refresh_icon()

    def _refresh_icon(self) -> None:
        color = resolve_theme_color(self._theme_data, self._color_role)
        self.setIcon(qta.icon(self._icon_name, color=color))
