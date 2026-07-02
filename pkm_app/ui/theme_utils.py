from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QByteArray, Qt
from core.constants.colors import Colors
from core.constants.icons import ICONS_DIR


def resolve_theme_color(theme_data: dict | None, key: str) -> str:
    """Return a theme color with a stable default before the first theme signal."""
    if theme_data and key in theme_data:
        return theme_data[key]
    return Colors.THEMES["dark"][key]


def to_qcolor(value: str) -> QColor:
    """CSS-style #RRGGBBAA hex'i Qt'nin bekledigi #AARRGGBB'ye cevirir."""
    if value.startswith("#") and len(value) == 9:
        return QColor(f"#{value[7:9]}{value[1:7]}")
    return QColor(value)


def with_alpha(color: str, alpha: str) -> str:
    if color.startswith("#") and len(color) == 7:
        return f"{color}{alpha}"
    return color


def valid_or_fallback(color: str | None, fallback: str) -> str:
    if color and QColor(color).isValid():
        return color
    return fallback


def load_theme_svg(svg_name: str, color_hex: str, size: int = 24) -> QIcon:
    """Belirtilen SVG dosyasini okur, icindeki currentColor yer tutucularini
    verilen renk ile degistirir ve dinamik olarak boyanmis bir QIcon doner.
    """
    svg_path = ICONS_DIR / svg_name
    if not svg_path.exists():
        return QIcon()
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        colored_content = content.replace("currentColor", color_hex)
        
        renderer = QSvgRenderer(QByteArray(colored_content.encode('utf-8')))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    except Exception:
        return QIcon()

