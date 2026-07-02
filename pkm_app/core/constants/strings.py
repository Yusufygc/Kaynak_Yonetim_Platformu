# -*- coding: utf-8 -*-
class AppStrings:
    APP_TITLE = "Kişisel Bilgi Yöneticisi"

    # Sidebar
    ALL_RESOURCES = "Tüm Kaynaklar"
    INBOX = "Gelen Kutusu"
    PLANNED = "Planlananlar"
    URL_SHOWCASE = "Bağlantı Vitrini"
    FAVORITES = "Favoriler"
    CATEGORIES = "Kategoriler"
    TAGS = "Etiketler"
    TOGGLE_THEME = "Tema Değiştir"

    # Toolbar
    SEARCH_PLACEHOLDER = "Ara..."
    ADD_NEW = "Yeni Ekle"

    # Ayarlar sayfası
    SETTINGS = "Ayarlar"
    SETTINGS_CATEGORIES_TAB = "Kategoriler"
    SETTINGS_TAGS_TAB = "Etiketler"
    CATEGORY_NAME = "Kategori adı"
    CATEGORY_COLOR = "Renk (#RRGGBB)"
    CATEGORY_ICON = "İkon (opsiyonel)"
    TAG_NAME = "Etiket adı"
    ADD = "Ekle"
    EDIT = "Düzenle"
    DELETE = "Sil"
    CONFIRM_DELETE = "Silmek için tekrar tıkla"

    # Detail panel
    OPEN_IN_BROWSER = "Tarayıcıda Aç"
    CLOSE_PANEL = "Kapat"
    STATUS_LABEL = "Durum"
    PROGRESS_LABEL = "İlerleme (%)"

    # Status values
    STATUS_PLANNED = "Planlandı"
    STATUS_IN_PROGRESS = "Devam Ediyor"
    STATUS_COMPLETED = "Tamamlandı"

    # Empty state
    EMPTY_STATE_MSG = "Burada henüz bir şey yok. Yeni Ekle'ye basarak ilk kaynağınızı oluşturun."

    # Form — Yeni Kaynak
    FORM_HEADER = "Yeni Kaynak Ekle"
    FORM_FIELD_TITLE = "Başlık *"
    FORM_FIELD_URL = "URL (opsiyonel)"
    FORM_FIELD_CATEGORY = "Kategori"
    FORM_FIELD_PRIORITY = "Öncelik"
    FORM_FIELD_TAGS = "Etiketler (virgülle ayır)"
    FORM_FIELD_CONTENT = "Not / Açıklama"
    FORM_PRIORITY_LOW = "3 — Düşük"
    FORM_PRIORITY_MEDIUM = "2 — Orta"
    FORM_PRIORITY_HIGH = "1 — Yüksek"
    FORM_CATEGORY_NONE = "— Seçiniz —"
    SAVE = "Kaydet"
    CANCEL = "İptal"

    # Form — Düzenle
    FORM_HEADER_EDIT = "Kaynağı Düzenle"
    FORM_FIELD_STATUS = "Durum"
    FORM_STATUS_INBOX = "Gelen Kutusu"
    FORM_STATUS_PLANNED = "Planlandı"
    FORM_STATUS_IN_PROGRESS = "Devam Ediyor"
    FORM_STATUS_COMPLETED = "Tamamlandı"
    EDIT_RESOURCE = "Düzenle"
    DELETE_RESOURCE = "Sil"
    CONFIRM_DELETE_RESOURCE = "Silmek için tekrar tıkla"
    SAVE_NOTES = "Notu Kaydet"

    # Errors
    ERR_INVALID_URL = "Geçersiz URL formatı."
    ERR_CATEGORY_NOT_FOUND = "Kategori bulunamadı."
    ERR_RESOURCE_NOT_FOUND = "Kaynak bulunamadı."
    ERR_DUPLICATE = "Bu isimde bir kayıt zaten mevcut."
    ERR_PROGRESS_RANGE = "İlerleme değeri 0-100 arasında olmalıdır."
    ERR_TITLE_REQUIRED = "Başlık boş bırakılamaz."
    ERR_HEX_FORMAT = "Renk formatı #RRGGBB olmalı (örnek: #3B82F6)."
    ERR_COLOR_REQUIRED = "Renk seçilmelidir."

    # Renk seçici
    PICK_COLOR_PLACEHOLDER = "Renk seç..."
    PICK_COLOR_TITLE = "Kategori rengini seçin"

    # Filtre çubuğu
    FILTER_CATEGORY = "Kategori"
    FILTER_TAG = "Etiket"
    FILTER_STATUS = "Durum"
    FILTER_PRIORITY = "Öncelik"
    FILTER_ANY = "Hepsi"
    FILTER_CLEAR = "Temizle"
    FILTER_TAG_PLACEHOLDER = "Etiket seç..."

    # Pin / Favori
    PIN_TOOLTIP = "Sabitle"
    UNPIN_TOOLTIP = "Sabitlemeyi kaldır"
    FAVORITE_TOOLTIP = "Favoriye ekle"
    UNFAVORITE_TOOLTIP = "Favoriden çıkar"
