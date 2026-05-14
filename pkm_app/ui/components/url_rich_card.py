from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from core.constants.icons import QtAwesomeIcons
from core.constants.strings import AppStrings
from core.events import event_bus
from models.resource import Resource
from utils.date_utils import format_date

_CARD_WIDTH = 260
_CARD_HEIGHT = 300
_THUMB_HEIGHT = 140


class UrlRichCard(QFrame):
    """URL kaynakları icin büyük, görsel odakli kart (URL Vitrini)."""

    def __init__(self, resource: Resource, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._resource_id = resource.id
        self._url = resource.url or ""
        self.setObjectName("UrlRichCard")
        self.setFixedSize(_CARD_WIDTH, _CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # Kategori/etiket rengine göre sol kenar
        border_color = self._resolve_border_color(resource)
        self.setStyleSheet(
            f"UrlRichCard {{ border-left: 4px solid {border_color}; border-radius: 8px; }}"
        )

        self._build_ui(resource)
        event_bus.theme_changed.connect(self._on_theme_changed)

    # ------------------------------------------------------------------ #
    # Yardımcılar
    # ------------------------------------------------------------------ #

    @staticmethod
    def _resolve_border_color(resource: Resource) -> str:
        if resource.category and resource.category.color_hex:
            return resource.category.color_hex
        if resource.tags:
            return "#82AAFF"
        return "#3B3B54"

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #

    def _build_ui(self, resource: Resource) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 10)
        layout.setSpacing(0)

        # --- Kapak görseli alanı ---
        self._thumb_label = QLabel()
        self._thumb_label.setObjectName("CardThumbnail")
        self._thumb_label.setFixedHeight(_THUMB_HEIGHT)
        self._thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumb_label.setStyleSheet("background: #2A2A3C; border-radius: 8px 8px 0 0;")

        thumbnail_url: str | None = (
            resource.extra_metadata.get("thumbnail") if resource.extra_metadata else None
        )
        if not thumbnail_url:
            # Görsel yoksa büyük ikon göster
            placeholder = qta.icon(QtAwesomeIcons.URL_SHOWCASE, color="#3B3B54").pixmap(48, 48)
            self._thumb_label.setPixmap(placeholder)

        layout.addWidget(self._thumb_label)

        # --- Başlık + açıklama ---
        text_area = QVBoxLayout()
        text_area.setContentsMargins(12, 8, 12, 4)
        text_area.setSpacing(4)

        meta_title: str = (
            resource.extra_metadata.get("og_title", resource.title)
            if resource.extra_metadata else resource.title
        )
        title_label = QLabel(meta_title)
        title_label.setObjectName("UrlCardTitle")
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(44)
        text_area.addWidget(title_label)

        meta_desc: str = (
            resource.extra_metadata.get("og_description", "")
            if resource.extra_metadata else ""
        )
        if meta_desc:
            desc_label = QLabel(meta_desc)
            desc_label.setObjectName("UrlCardDesc")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(36)
            text_area.addWidget(desc_label)

        layout.addLayout(text_area)
        layout.addStretch()

        # --- Alt bar: kategori rozeti + aç butonu ---
        bottom = QHBoxLayout()
        bottom.setContentsMargins(12, 0, 12, 0)
        bottom.setSpacing(6)

        if resource.category:
            cat_badge = QLabel(resource.category.name)
            cat_badge.setObjectName("UrlCardCatBadge")
            border_color = resource.category.color_hex or "#82AAFF"
            cat_badge.setStyleSheet(
                f"background: {border_color}22; color: {border_color};"
                "border-radius: 4px; padding: 2px 6px; font-size: 10px;"
            )
            bottom.addWidget(cat_badge)

        bottom.addStretch()

        self._open_btn = QPushButton(AppStrings.OPEN_IN_BROWSER)
        self._open_btn.setObjectName("UrlOpenButton")
        self._open_btn.setIcon(qta.icon(QtAwesomeIcons.OPEN_BROWSER, color="#82AAFF"))
        self._open_btn.clicked.connect(self._open_in_browser)
        bottom.addWidget(self._open_btn)

        layout.addLayout(bottom)

    # ------------------------------------------------------------------ #
    # Olaylar
    # ------------------------------------------------------------------ #

    def mousePressEvent(self, event) -> None:
        # Butona tıklanmadıysa detay panelini aç
        if not self._open_btn.underMouse():
            event_bus.resource_selected.emit(self._resource_id)
        super().mousePressEvent(event)

    def _open_in_browser(self) -> None:
        if self._url:
            QDesktopServices.openUrl(QUrl(self._url))

    def _on_theme_changed(self, theme_data: dict) -> None:
        color = theme_data.get("accent_color", "#82AAFF")
        self._open_btn.setIcon(qta.icon(QtAwesomeIcons.OPEN_BROWSER, color=color))
