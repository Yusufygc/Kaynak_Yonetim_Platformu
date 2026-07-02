# Arayüz (UI) İskeleti ve Layout

## Genel Mimari: Three-Pane (Master-Detail)

`MainWindow(QMainWindow)` üç sütunlu yapı; sütunlar arası yatay `QSplitter`.

| Sütun | Bileşen | Dosya |
|-------|---------|-------|
| Sol | Sidebar (navigasyon) | `ui/components/sidebar.py` |
| Orta | `ContentWorkspace` (3 sayfa + filter dispatch) | `ui/views/content_workspace.py` |
| Sağ | `DetailView` (3 sayfa stack koordinatörü) | `ui/views/detail_view.py` |

### UI Katmanları (2026-05-17 refaktör sonrası)

```
MainWindow (ince compose, ~55 satır)
├── Sidebar
├── ContentWorkspace
│     ├── ContentView (ResourceCard listesi)
│     ├── SettingsView (kategori/etiket CRUD)
│     └── UrlShowcaseView (UrlRichCard)
└── DetailView (QStackedWidget koordinatörü)
      ├── EmptyDetail (ui/components/empty_detail.py)
      ├── ResourceDetailPanel (ui/components/resource_detail_panel.py)
      └── ResourceForm (ui/components/resource_form.py)

ResourceFlow (ui/controllers/resource_flow.py)
  ↳ event_bus + Workspace/Detail sinyalleri → MainController çağrıları
```

- **MainWindow** sadece pencere iskeletini kurar; iş mantığı yok.
- **ContentWorkspace** `apply_filter(filter_key)` sözlük tabanlı dispatch yapar; `refresh()` aktif filtreyi yeniden uygular.
- **ResourceFlow** UI ile servis arası koordinatör; widget değil, sinyal yönlendirici. `wire()` ile başlatılır.
- **DetailView** ince stack koordinatörü; alt panel sinyallerini aynı isimle dışarı relay eder — dış API kırılmaz.

**Kural:** Hard-coded renk/font yasaktır. Tüm görsel değerler `core/constants/` veya QSS'ten gelir.

---

## Sol — Sidebar (`ui/components/sidebar.py`)

Sabit genişlik: 220 px. Sadece navigasyon — CRUD işlemleri buraya eklenmez.
Navigasyon item'ları qtawesome ikonlarıyla gösterilir; seçili item accent rengine, diğerleri tema ikon rengine döner.

`_STATIC_ITEMS` ile tanımlı 6 nav öğesi:

| Etiket | Filter Key | Yönlendirme |
|--------|-----------|-------------|
| Tüm Kaynaklar | `"all"` | ContentView — tüm kaynaklar |
| Gelen Kutusu | `"inbox"` | ContentView — `INBOX` statüslü kaynaklar |
| Planlananlar | `"planned"` | ContentView — `PLANNED` statüslü kaynaklar |
| Favoriler | `"favorites"` | ContentView — `is_favorite=True` kayıtlar (her listede pinli üstte) |
| Bağlantı Vitrini | `"url_showcase"` | UrlShowcaseView — URL'li kaynaklar |
| Ayarlar | `"settings"` | SettingsView — kategori/etiket CRUD |

Alt kısımda **Tema Değiştir** butonu. Sidebar `event_bus.sidebar_filter_changed(filter_key)` yayınlar; `ResourceFlow._on_filter_changed` yakalar → `ContentWorkspace.apply_filter()`.

---

## Orta — `ContentWorkspace` (QStackedWidget)

`MainWindow._build_ui` içinde `QSplitter`'ın sol widget'ı. Üç sayfa:

| Index | Widget | Ne zaman gösterilir |
|-------|--------|---------------------|
| 0 | `ContentView` | Tüm filtreler (all/inbox/planned/search:…) |
| 1 | `SettingsView` | `"settings"` filtresi |
| 2 | `UrlShowcaseView` | `"url_showcase"` filtresi |

### ContentView (`ui/views/content_view.py`)
- **Üst Bar:** `SearchBar` + "Yeni Ekle" butonu
- **FilterBar** (`ui/components/filter_bar.py`): Kategori dropdown + çoklu Etiket dropdown + Durum chip'leri + Öncelik chip'leri + Temizle. `filters_changed(dict)` sinyali → `ContentWorkspace._on_filters_changed` → aktif sayfa yeniden çizilir. Filtre şeması: `{"category_id", "tag_ids", "statuses", "priorities"}`. Aynı bileşen `UrlShowcaseView`'da da kullanılır.
  - **Görsel tasarım (2026-07-02):** Gövdeden ayrık "yükseltilmiş navbar kartı" — kendi arka planı (`surface_elevated`), kenarlığı, 12px yuvarlak köşesi ve `QGraphicsDropShadowEffect` gölgesi var (`Colors.SHADOW`, tema değişince güncellenir). `QFrame` alt sınıfı olduğu için QSS `background-color`/`border-radius`'un boyanması `WA_StyledBackground` attribute'una bağlı — bu attribute set edilmeden QSS arka planı yoksayılır (Qt gotcha'sı). Filtre grupları arası ince `#FilterSeparator` ayraçlarla görsel olarak bölünür. "Temizle" butonu hiçbir filtre aktif değilken otomatik devre dışı kalır (`_update_clear_button_state()`), gereksiz tıklamayı önler.
  - `%RRGGBBAA` (CSS-stili, alfa sonda) tema renklerini (`shadow_color` gibi) Qt'nin beklediği `#AARRGGBB` formatına çeviren `ui/theme_utils.py::to_qcolor()` — `ui/components/painted.py`'deki eski özel `_to_color` fonksiyonundan buraya taşındı (DRY), `painted.py` artık buradan import ediyor.
- **Inline Banner:** `InlineBanner` — başarı/hata bildirimi, 3.5 sn sonra kaybolur
- **İçerik:** `QScrollArea` + `FlowLayout` içinde `ResourceCard` widget'ları
- **Kart üstü pin/favori:** `PinButton` + `FavoriteButton` (`ui/components/card_icon_button.py`). Tıklama event_bus üzerinden `ResourceFlow → controller.toggle_pin/toggle_favorite`. Pinli kayıt her sorguda en üste gelir.

### SettingsView (`ui/views/settings_view.py`)
`QTabWidget`, iki sekme:
- **Kategoriler:** Scroll liste (`CategoryRow`) + alt kısımda inline ekleme formu (ad/renk/ikon). Renk seçimi `ColorPickerButton` ile interaktif yapılır.
- **Etiketler:** Scroll liste (`TagRow`) + inline ekleme formu (ad)
Her `CategoryRow` / `TagRow`: inline düzenle + 2-tıklı sil. `QDialog/QMessageBox` kullanılmaz.

### UrlShowcaseView (`ui/views/url_showcase_view.py`)
- `FlowLayout` içinde `UrlRichCard` bileşenleri
- Sadece `url` alanı dolu kaynaklar gösterilir
- `load_resources(list)` — `ContentWorkspace._show_url_showcase` tarafından çağrılır

---

## Sağ — DetailView (`ui/views/detail_view.py`)

İnce `QStackedWidget` koordinatörü (~95 satır). Üç sayfa ayrı bileşenlerden gelir:

| Index | Sayfa | Bileşen | Tetikleyici |
|-------|-------|---------|------------|
| 0 | Boş durum | `EmptyDetail` (`ui/components/empty_detail.py`) | `clear()` çağrıldığında |
| 1 | Kaynak görüntüleme | `ResourceDetailPanel` (`ui/components/resource_detail_panel.py`) | `load_resource(resource)` |
| 2 | Kaynak formu | `ResourceForm` (`ui/components/resource_form.py`) | `show_form(...)` / `show_form_edit(...)` |

DetailView yalnızca sayfa geçişini ve sinyal relay'ini yönetir; widget mantığı alt bileşenlerde.

### Görüntüleme paneli (`ResourceDetailPanel`)
- Başlık etiketi (read-only)
- URL butonu (tıklanabilir, tarayıcıda açar)
- Durum `QComboBox` — değişince `status_updated(int, ResourceStatus)` → `ResourceFlow._on_status_updated`
- İlerleme `QSpinBox` — değişince `progress_updated(int, int)` → `controller.update_progress`
- Notlar `QTextEdit` (düzenlenebilir) + **"Notu Kaydet"** butonu → `content_updated(int, str)` → `ResourceFlow._on_content_updated`
- **"Düzenle"** butonu → `edit_requested(int)` → `ResourceFlow._on_edit_requested` → form sayfası dolu açılır
- **"Sil"** butonu → inline 2-tıklı onay → `delete_requested(int)` → `ResourceFlow._on_delete_requested`
- Tema değişiminde `event_bus.theme_changed` panel içinden dinlenir, kapatma ikonu refresh'lenir.

### Form sayfası (index 2) — `ResourceForm`
**Hem ekleme hem düzenleme** için kullanılır (DRY):
- `reset_for_new()` + `load_categories(list)` → yeni kaynak modu (header: "Yeni Kaynak Ekle", status default INBOX)
- `load_resource(resource, categories)` → düzenleme modu (header: "Kaynağı Düzenle", alanlar dolu)
- `submitted(dict)` sinyali: `resource_id` anahtarı varsa güncelleme, yoksa ekleme

`ResourceFlow._on_form_submitted` ayrımı yapar → `controller.add_resource` veya `controller.update_resource`.

---

## Kart Tipleri

| Tip | Dosya | Kullanım |
|-----|-------|----------|
| `ResourceCard` | `ui/components/resource_card.py` | ContentView (all/inbox/planned/search) |
| `UrlRichCard` | `ui/components/url_rich_card.py` | UrlShowcaseView |

Kartlar `AccentFrame` tabanlıdır: sol accent şeridi painter ile çizilir, hover durumunda kısa shadow/lift animasyonu alır. `ResourceCard` vurgu rengi kuralı: Kategori rengi > Durum rengi (fallback) şeklindedir. Durum/tag/kategori rozetleri `ColorBadge`, kategori renk önizlemeleri `ColorSwatch` ile çizilir.

---

## Boş Durum (Empty State)
Sonuç yokken `ContentView.show_empty_state(True)` çağrılır — scroll alanı gizlenir, ortalanmış `EmptyStateLabel` gösterilir.

---

## Sinyaller Özeti (DetailView)

| Sinyal | Tip | Alıcı |
|--------|-----|-------|
| `progress_updated` | `Signal(int, int)` | `controller.update_progress` |
| `status_updated` | `Signal(int, object)` | `ResourceFlow._on_status_updated` → `controller.update_resource` |
| `content_updated` | `Signal(int, str)` | `ResourceFlow._on_content_updated` → `controller.update_resource` |
| `form_submitted` | `Signal(dict)` | `ResourceFlow._on_form_submitted` |
| `edit_requested` | `Signal(int)` | `ResourceFlow._on_edit_requested` |
| `delete_requested` | `Signal(int)` | `ResourceFlow._on_delete_requested` |

## İlgili Sayfalar
[[dizin_yapisi]] · [[event_bus]] · [[url_vitrin]] · [[tema_yonetimi]] · [[core_servisler]] · [[veritabani_semasi]]
