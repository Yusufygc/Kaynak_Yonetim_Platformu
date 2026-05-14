from pathlib import Path

ICONS_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "icons"


class QtAwesomeIcons:
    """qtawesome ikon isimleri."""
    ALL_RESOURCES = "fa5s.layer-group"
    INBOX = "fa5s.inbox"
    PLANNED = "fa5s.clock"
    URL_SHOWCASE = "fa5s.globe"
    CATEGORY = "fa5s.folder"
    TAG = "fa5s.tag"
    ADD = "fa5s.plus-circle"
    SEARCH = "fa5s.search"
    OPEN_BROWSER = "fa5s.external-link-alt"
    CLOSE = "fa5s.times"
    THEME_DARK = "fa5s.moon"
    THEME_LIGHT = "fa5s.sun"
    PINNED = "fa5s.thumbtack"
    DELETE = "fa5s.trash-alt"
    EDIT = "fa5s.pen"
    SETTINGS = "fa5s.cog"


class CustomIcons:
    """SVG ikonlar icin tam dosya yollari."""

    @staticmethod
    def get(filename: str) -> str:
        return str(ICONS_DIR / filename)
