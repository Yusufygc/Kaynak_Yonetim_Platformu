from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPaintEvent, QPen
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QWidget


class AccentFrame(QFrame):
    """Frame with a painter-rendered left accent strip."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._accent_color = QColor()
        self._accent_width = 4
        self._hover_progress = 0.0
        self._shadow_color = QColor()
        self._shadow_effect = QGraphicsDropShadowEffect(self)
        self._shadow_effect.setBlurRadius(0)
        self._shadow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow_effect)
        self._hover_animation = QPropertyAnimation(self, b"hoverProgress", self)
        self._hover_animation.setDuration(140)
        self._hover_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_accent_color(self, color: str) -> None:
        self._accent_color = _to_color(color)
        self.update()

    def set_shadow_color(self, color: str) -> None:
        self._shadow_color = _to_color(color)
        self._apply_shadow()

    def hoverProgress(self) -> float:
        return self._hover_progress

    def setHoverProgress(self, value: float) -> None:
        self._hover_progress = max(0.0, min(1.0, value))
        self._apply_shadow()
        self.update()

    hoverProgress = Property(float, hoverProgress, setHoverProgress)

    def enterEvent(self, event) -> None:
        self._animate_hover(1.0)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._animate_hover(0.0)
        super().leaveEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)
        if not self._accent_color.isValid():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        color = QColor(self._accent_color)
        if self._hover_progress:
            color = color.lighter(100 + int(self._hover_progress * 25))
        width = self._accent_width + int(self._hover_progress * 2)
        painter.fillRect(0, 0, width, self.height(), color)

    def _animate_hover(self, target: float) -> None:
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(target)
        self._hover_animation.start()

    def _apply_shadow(self) -> None:
        if not self._shadow_color.isValid():
            return
        self._shadow_effect.setColor(self._shadow_color)
        self._shadow_effect.setBlurRadius(4 + self._hover_progress * 12)
        self._shadow_effect.setOffset(0, self._hover_progress * 3)


class ColorBadge(QWidget):
    """Small text badge with painter-rendered dynamic colors."""

    def __init__(
        self,
        text: str,
        foreground: str,
        background: str,
        radius: int = 4,
        horizontal_padding: int = 6,
        vertical_padding: int = 2,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._text = text
        self._foreground = _to_color(foreground)
        self._background = _to_color(background)
        self._radius = radius
        self._horizontal_padding = horizontal_padding
        self._vertical_padding = vertical_padding
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setMinimumHeight(self.sizeHint().height())

    def set_colors(self, foreground: str, background: str) -> None:
        self._foreground = _to_color(foreground)
        self._background = _to_color(background)
        self.update()

    def text(self) -> str:
        return self._text

    def sizeHint(self) -> QSize:
        metrics = QFontMetrics(self.font())
        return QSize(
            metrics.horizontalAdvance(self._text) + self._horizontal_padding * 2,
            metrics.height() + self._vertical_padding * 2,
        )

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._background)
        painter.drawRoundedRect(self.rect(), self._radius, self._radius)
        painter.setPen(QPen(self._foreground))
        font = painter.font()
        font.setWeight(QFont.Weight.DemiBold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._text)


class ColorSwatch(QWidget):
    """Painter-rendered color preview for user supplied category colors."""

    def __init__(
        self,
        color_hex: str,
        fallback_color: str,
        border_color: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._fallback_color = fallback_color
        self._border_color = border_color
        self._color = self._resolve_color(color_hex)
        self.setFixedSize(18, 18)

    def set_color(self, color_hex: str, fallback_color: str, border_color: str) -> None:
        self._fallback_color = fallback_color
        self._border_color = border_color
        self._color = self._resolve_color(color_hex)
        self.update()

    def sizeHint(self) -> QSize:
        return QSize(18, 18)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(_to_color(self._border_color)))
        painter.setBrush(self._color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 3, 3)

    def _resolve_color(self, color_hex: str) -> QColor:
        color = _to_color(color_hex)
        return color if color.isValid() else _to_color(self._fallback_color)


def _to_color(value: str) -> QColor:
    # Convert CSS-style #RRGGBBAA to Qt-friendly #AARRGGBB.
    if value.startswith("#") and len(value) == 9:
        return QColor(f"#{value[7:9]}{value[1:7]}")
    return QColor(value)
