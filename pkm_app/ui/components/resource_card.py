from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import qtawesome as qta

from core.constants.icons import QtAwesomeIcons
from core.events import event_bus
from models.resource import Resource, ResourceStatus
from utils.date_utils import format_date

_CARD_WIDTH = 240
_CARD_HEIGHT = 160

_STATUS_COLORS = {
    ResourceStatus.PLANNED: "#82AAFF",
    ResourceStatus.IN_PROGRESS: "#FFCB6B",
    ResourceStatus.COMPLETED: "#C3E88D",
}

_STATUS_LABELS = {
    ResourceStatus.PLANNED: "Planlandı",
    ResourceStatus.IN_PROGRESS: "Devam Ediyor",
    ResourceStatus.COMPLETED: "Tamamlandı",
}


class ResourceCard(QFrame):
    """Standart metin/not kaynaklari icin sabit boyutlu kart."""

    def __init__(self, resource: Resource, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._resource_id = resource.id
        self.setObjectName("ResourceCard")
        self.setFixedSize(_CARD_WIDTH, _CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        accent = _STATUS_COLORS.get(resource.status, "#82AAFF")
        self.setStyleSheet(
            f"ResourceCard {{ border-left: 4px solid {accent}; border-radius: 8px; }}"
        )

        self._build_ui(resource)
        event_bus.theme_changed.connect(self._on_theme_changed)

    def _build_ui(self, resource: Resource) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # --- Üst satır: kategori ikonu + durum rozeti ---
        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        cat_icon_label = QLabel()
        cat_icon_label.setObjectName("CardCatIcon")
        icon_name = (
            resource.category.icon
            if resource.category and resource.category.icon
            else QtAwesomeIcons.CATEGORY
        )
        try:
            cat_icon_label.setPixmap(
                qta.icon(icon_name, color="#A0A0B0").pixmap(16, 16)
            )
        except Exception:
            cat_icon_label.setPixmap(
                qta.icon(QtAwesomeIcons.CATEGORY, color="#A0A0B0").pixmap(16, 16)
            )
        top_row.addWidget(cat_icon_label)
        top_row.addStretch()

        status_label = QLabel(_STATUS_LABELS.get(resource.status, ""))
        status_label.setObjectName("CardStatusBadge")
        status_color = _STATUS_COLORS.get(resource.status, "#82AAFF")
        status_label.setStyleSheet(
            f"background: {status_color}22; color: {status_color};"
            "border-radius: 4px; padding: 1px 6px; font-size: 10px;"
        )
        top_row.addWidget(status_label)
        layout.addLayout(top_row)

        # --- Başlık ---
        title = QLabel(resource.title)
        title.setObjectName("CardTitle")
        title.setWordWrap(True)
        title.setMaximumHeight(48)
        title.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(title)

        layout.addStretch()

        # --- Alt satır: tarih + etiketler ---
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(4)

        date_label = QLabel(format_date(resource.created_at))
        date_label.setObjectName("CardDate")
        bottom_row.addWidget(date_label)
        bottom_row.addStretch()

        for tag in resource.tags[:3]:
            badge = QLabel(f"#{tag.name}")
            badge.setObjectName("CardTagBadge")
            badge.setStyleSheet(
                "background: #3B3B54; color: #A0A0B0;"
                "border-radius: 4px; padding: 1px 5px; font-size: 10px;"
            )
            bottom_row.addWidget(badge)

        layout.addLayout(bottom_row)

    def mousePressEvent(self, event) -> None:
        event_bus.resource_selected.emit(self._resource_id)
        super().mousePressEvent(event)

    def _on_theme_changed(self, theme_data: dict) -> None:
        # Etiket rozet renkleri temadan bagımsız (durum rengi sabit);
        # arka plan ve kenarlıklar QSS üzerinden güncellenir.
        pass
