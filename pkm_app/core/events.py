from PySide6.QtCore import QObject, Signal


class _EventBus(QObject):
    """Merkezi olay yonetici — Singleton + Observer deseni.

    UI bilesenleri birbirini dogrudan referans almaz;
    tüm durum degisiklikleri bu sinif üzerinden akar.
    """

    # --- Kaynak (Resource) sinyalleri ---
    resource_added = Signal(int)      # yeni kaynak ID'si
    resource_updated = Signal(int)    # güncellenen kaynak ID'si
    resource_deleted = Signal(int)    # silinen kaynak ID'si

    # --- Kategori sinyalleri ---
    category_added = Signal(int)
    category_updated = Signal(int)
    category_deleted = Signal(int)

    # --- Etiket sinyalleri ---
    tag_added = Signal(int)
    tag_deleted = Signal(int)

    # --- UI etkilesim sinyalleri ---
    resource_selected = Signal(int)       # karta tiklandı → sag panel ac
    search_query_changed = Signal(str)    # arama cubugu metni degisti
    sidebar_filter_changed = Signal(str)  # sol menü secimi degisti (kategori adi veya sabit filtre)

    # --- Tema sinyali ---
    theme_changed = Signal(dict)          # aktif tema renk sözlügü


event_bus = _EventBus()
