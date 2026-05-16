from core.paths import resource_path

ICONS_DIR = resource_path("assets", "icons")


class QtAwesomeIcons:
    """qtawesome ikon isimleri."""
    ALL = "fa5s.layer-group"
    INBOX = "fa5s.inbox"
    PLANNED = "fa5s.clock"
    FAVORITES = "fa5s.star"
    URL_SHOWCASE = "fa5s.globe"
    SETTINGS = "fa5s.cog"
    IDEAS = "fa5s.lightbulb"

    # Arama & Input
    SEARCH = "fa5s.search"
    OPEN_BROWSER = "fa5s.external-link-alt"
    CLOSE = "fa5s.times"
    THEME_DARK = "fa5s.moon"
    THEME_LIGHT = "fa5s.sun"
    CATEGORY = "fa5s.folder"
    TAG = "fa5s.tag"
    ADD = "fa5s.plus-circle"
    PINNED = "fa5s.thumbtack"
    FAVORITE = "fa5s.star"
    FAVORITE_OUTLINE = "fa5s.star"  # qtawesome free FA5 regular yok; solid kullan, renk farki ile
    DELETE = "fa5s.trash-alt"
    EDIT = "fa5s.pen"
    SETTINGS = "fa5s.cog"
    FILTER_CLEAR = "fa5s.times-circle"


class CustomIcons:
    """SVG ikonlar icin tam dosya yollari."""

    @staticmethod
    def get(filename: str) -> str:
        return str(ICONS_DIR / filename)
