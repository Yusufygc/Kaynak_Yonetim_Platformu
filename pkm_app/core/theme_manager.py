from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication

from core.config import settings
from core.constants.colors import Colors
from core.logger import log

if TYPE_CHECKING:
    pass

_STYLES_DIR = Path(__file__).resolve().parent.parent / "assets" / "styles"


class _ThemeManager:
    """Singleton tema yoneticisi.

    QSS sablonlarindaki {{ anahtar }} yer tutucularini aktif temanin
    renkleriyle doldurur ve QApplication'a uygular.
    """

    _instance: "_ThemeManager | None" = None

    def __new__(cls) -> "_ThemeManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current_theme: dict[str, str] = {}
        return cls._instance

    def apply_theme(self, theme_name: str) -> None:
        theme = Colors.THEMES.get(theme_name)
        if theme is None:
            log.warning("Bilinmeyen tema: %s. 'dark' kullaniliyor.", theme_name)
            theme = Colors.THEMES["dark"]

        self._current_theme = theme
        qss = self._build_qss(theme)
        QApplication.instance().setStyleSheet(qss)  # type: ignore[union-attr]

        # Event Bus burada import ediliyor — dairesel import'tan kacmak icin.
        from core.events import event_bus
        event_bus.theme_changed.emit(theme)
        log.info("Tema uygulandi: %s", theme["name"])

    def toggle_theme(self) -> None:
        current = self._current_theme.get("name", "dark")
        next_theme = "light" if current == "dark" else "dark"
        self.apply_theme(next_theme)

    @property
    def current_theme(self) -> dict[str, str]:
        return self._current_theme

    def _build_qss(self, theme: dict[str, str]) -> str:
        qss_parts: list[str] = []
        for qss_file in sorted(_STYLES_DIR.glob("*.qss")):
            try:
                raw = qss_file.read_text(encoding="utf-8")
                for key, value in theme.items():
                    raw = raw.replace("{{" + key + "}}", value)
                qss_parts.append(raw)
            except OSError as exc:
                log.error("QSS dosyasi okunamadi: %s — %s", qss_file, exc)
        return "\n".join(qss_parts)


theme_manager = _ThemeManager()
