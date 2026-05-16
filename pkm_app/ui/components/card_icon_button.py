from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QPushButton, QWidget

import qtawesome as qta

from core.constants.colors import Colors
from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from ui.theme_utils import resolve_theme_color


class _CardIconButton(QPushButton):
    """Kart kose ikonu icin temel toggle butonu (pin / favori)."""

    _ICON_SIZE = 14
    _BUTTON_SIZE = 22

    def __init__(
        self,
        resource_id: int,
        active: bool,
        icon_active: str,
        icon_inactive: str,
        tooltip_active: str,
        tooltip_inactive: str,
        signal_name: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._resource_id = resource_id
        self._active = bool(active)
        self._icon_active = icon_active
        self._icon_inactive = icon_inactive
        self._tooltip_active = tooltip_active
        self._tooltip_inactive = tooltip_inactive
        self._signal_name = signal_name
        self._theme_data: dict | None = None

        self.setObjectName("CardIconButton")
        self.setFixedSize(self._BUTTON_SIZE, self._BUTTON_SIZE)
        self.setIconSize(QSize(self._ICON_SIZE, self._ICON_SIZE))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFlat(True)

        self._refresh()
        event_bus.theme_changed.connect(self._on_theme_changed)
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self) -> None:
        signal = getattr(event_bus, self._signal_name)
        signal.emit(self._resource_id)

    def _on_theme_changed(self, theme_data: dict) -> None:
        self._theme_data = theme_data
        self._refresh()

    def _refresh(self) -> None:
        if self._active:
            color = resolve_theme_color(self._theme_data, Colors.ACCENT)
            self.setIcon(qta.icon(self._icon_active, color=color))
            self.setToolTip(self._tooltip_active)
        else:
            color = resolve_theme_color(self._theme_data, Colors.TEXT_SECONDARY)
            self.setIcon(qta.icon(self._icon_inactive, color=color))
            self.setToolTip(self._tooltip_inactive)


class PinButton(_CardIconButton):
    def __init__(self, resource_id: int, pinned: bool, parent: QWidget | None = None) -> None:
        super().__init__(
            resource_id=resource_id,
            active=pinned,
            icon_active=QtAwesomeIcons.PINNED,
            icon_inactive=QtAwesomeIcons.PINNED,
            tooltip_active=AppStrings.UNPIN_TOOLTIP,
            tooltip_inactive=AppStrings.PIN_TOOLTIP,
            signal_name="resource_pin_toggle_requested",
            parent=parent,
        )


class FavoriteButton(_CardIconButton):
    def __init__(self, resource_id: int, favorited: bool, parent: QWidget | None = None) -> None:
        super().__init__(
            resource_id=resource_id,
            active=favorited,
            icon_active=QtAwesomeIcons.FAVORITE,
            icon_inactive=QtAwesomeIcons.FAVORITE_OUTLINE,
            tooltip_active=AppStrings.UNFAVORITE_TOOLTIP,
            tooltip_inactive=AppStrings.FAVORITE_TOOLTIP,
            signal_name="resource_favorite_toggle_requested",
            parent=parent,
        )
