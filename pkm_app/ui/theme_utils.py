from core.constants.colors import Colors
from PySide6.QtGui import QColor


def resolve_theme_color(theme_data: dict | None, key: str) -> str:
    """Return a theme color with a stable default before the first theme signal."""
    if theme_data and key in theme_data:
        return theme_data[key]
    return Colors.THEMES["dark"][key]


def with_alpha(color: str, alpha: str) -> str:
    if color.startswith("#") and len(color) == 7:
        return f"{color}{alpha}"
    return color


def valid_or_fallback(color: str | None, fallback: str) -> str:
    if color and QColor(color).isValid():
        return color
    return fallback
