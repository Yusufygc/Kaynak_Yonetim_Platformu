from core.themes.dark import DARK_THEME
from core.themes.light import LIGHT_THEME


class Colors:
    """
    Aktif tema sozlugune erisim icin yardimci sinif.
    Dogrudan HEX kullanmak yerine ThemeManager uzerinden renk alinmalidir;
    bu sinif sadece tema anahtarlarini sabit olarak tutar.
    """

    # Tema anahtar sabitleri
    BG_PRIMARY = "bg_primary"
    BG_SECONDARY = "bg_secondary"
    TEXT_PRIMARY = "text_primary"
    TEXT_SECONDARY = "text_secondary"
    ACCENT = "accent_color"
    BORDER = "border_color"
    ICON = "icon_color"

    THEMES = {
        "dark": DARK_THEME,
        "light": LIGHT_THEME,
    }
