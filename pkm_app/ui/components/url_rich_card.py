from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from core.constants.colors import Colors
from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from models import Resource
from ui.components.painted import AccentFrame, ColorBadge
from ui.theme_utils import resolve_theme_color, valid_or_fallback, with_alpha

_CARD_WIDTH = 320
_CARD_HEIGHT = 380
_THUMB_HEIGHT = 180


class UrlRichCard(AccentFrame):
    """URL kaynaklari icin buyuk, gorsel odakli kart (URL Vitrini)."""

    def __init__(self, resource: Resource, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._resource = resource
        self._resource_id = resource.id
        self._url = resource.url or ""
        self._theme_data: dict | None = None
        self._network_manager: QNetworkAccessManager | None = None
        self._open_btn: QPushButton | None = None
        self._thumb_label: QLabel | None = None
        self._desc_label: QLabel | None = None
        self._thumbnail_url: str | None = None
        self._thumbnail_loaded = False

        self.setObjectName("UrlRichCard")
        self.setFixedSize(_CARD_WIDTH, _CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_accent_color(self._resolve_border_color(resource))
        self.set_shadow_color(resolve_theme_color(self._theme_data, Colors.SHADOW))

        self._build_ui(resource)
        event_bus.theme_changed.connect(self._on_theme_changed)

    def _resolve_border_color(self, resource: Resource) -> str:
        if resource.category and resource.category.color_hex:
            return valid_or_fallback(
                resource.category.color_hex,
                resolve_theme_color(self._theme_data, Colors.CATEGORY_FALLBACK),
            )
        if resource.tags:
            return resolve_theme_color(self._theme_data, Colors.ACCENT)
        return resolve_theme_color(self._theme_data, Colors.BORDER)

    def _build_ui(self, resource: Resource) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(0)

        self._thumb_label = QLabel()
        self._thumb_label.setObjectName("CardThumbnail")
        self._thumb_label.setFixedHeight(_THUMB_HEIGHT)
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._thumbnail_url = (
            resource.extra_metadata.get("thumbnail") if resource.extra_metadata else None
        )
        if self._thumbnail_url:
            self._load_thumbnail(self._thumbnail_url)
        else:
            self._set_thumbnail_placeholder()

        layout.addWidget(self._thumb_label)

        text_area = QVBoxLayout()
        text_area.setContentsMargins(14, 10, 14, 6)
        text_area.setSpacing(6)

        meta_title: str = (
            resource.extra_metadata.get("og_title", resource.title)
            if resource.extra_metadata else resource.title
        )
        title_label = QLabel(meta_title)
        title_label.setObjectName("UrlCardTitle")
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(70)
        text_area.addWidget(title_label)

        meta_desc: str = (
            resource.extra_metadata.get("og_description", "")
            if resource.extra_metadata else ""
        ) or (resource.content or "")
        if meta_desc:
            self._desc_label = QLabel(meta_desc)
            self._desc_label.setObjectName("UrlCardDesc")
            self._desc_label.setWordWrap(True)
            self._desc_label.setMaximumHeight(68)
            text_area.addWidget(self._desc_label)

        layout.addLayout(text_area)
        layout.addStretch()

        bottom = QHBoxLayout()
        bottom.setContentsMargins(14, 0, 14, 0)
        bottom.setSpacing(8)

        if resource.category:
            category_color = valid_or_fallback(
                resource.category.color_hex,
                resolve_theme_color(self._theme_data, Colors.CATEGORY_FALLBACK),
            )
            bottom.addWidget(
                ColorBadge(
                    resource.category.name,
                    category_color,
                    with_alpha(category_color, "22"),
                )
            )

        bottom.addStretch()

        self._open_btn = QPushButton(AppStrings.OPEN_IN_BROWSER)
        self._open_btn.setObjectName("UrlOpenButton")
        self._open_btn.clicked.connect(self._open_in_browser)
        self._update_open_icon()
        bottom.addWidget(self._open_btn)

        layout.addLayout(bottom)

    def mousePressEvent(self, event) -> None:
        if self._open_btn is not None and not self._open_btn.underMouse():
            event_bus.resource_selected.emit(self._resource_id)
        super().mousePressEvent(event)

    def _open_in_browser(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))

    def _on_theme_changed(self, theme_data: dict) -> None:
        self._theme_data = theme_data
        self.set_accent_color(self._resolve_border_color(self._resource))
        self.set_shadow_color(resolve_theme_color(self._theme_data, Colors.SHADOW))
        self._update_open_icon()
        if not self._thumbnail_loaded:
            self._set_thumbnail_placeholder()
        self.update()

    def _update_open_icon(self) -> None:
        if self._open_btn is None:
            return
        color = resolve_theme_color(self._theme_data, Colors.ACCENT)
        self._open_btn.setIcon(qta.icon(QtAwesomeIcons.OPEN_BROWSER, color=color))

    def _set_thumbnail_placeholder(self) -> None:
        if self._thumb_label is None:
            return
        color = resolve_theme_color(self._theme_data, Colors.BORDER)
        placeholder = qta.icon(QtAwesomeIcons.URL_SHOWCASE, color=color).pixmap(48, 48)
        self._thumb_label.setPixmap(placeholder)

    def _load_thumbnail(self, thumbnail_url: str) -> None:
        self._set_thumbnail_placeholder()
        url = QUrl(thumbnail_url)
        if not url.isValid():
            return

        self._network_manager = QNetworkAccessManager(self)
        reply = self._network_manager.get(QNetworkRequest(url))
        reply.finished.connect(lambda: self._on_thumbnail_loaded(reply))

    def _on_thumbnail_loaded(self, reply: QNetworkReply) -> None:
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                return
            pixmap = QPixmap()
            if not pixmap.loadFromData(bytes(reply.readAll())):
                return
            scaled = pixmap.scaled(
                _CARD_WIDTH,
                _THUMB_HEIGHT,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            if self._thumb_label is not None:
                self._thumb_label.setPixmap(scaled)
                self._thumbnail_loaded = True
        finally:
            reply.deleteLater()
