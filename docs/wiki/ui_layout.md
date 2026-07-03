# Arayüz (UI) İskeleti ve Layout

## Genel Mimari: Three-Pane (Master-Detail)

`MainWindow(QMainWindow)` üç sütunlu yapı; sütunlar arası yatay `QSplitter`.

| Sütun | Bileşen | Dosya |
|-------|---------|-------|
| Sol | Sidebar (navigasyon) | `ui/components/sidebar.py` |
| Orta | `ContentWorkspace` (2 sayfa + filter dispatch) | `ui/views/content_workspace.py` |
| Sağ | `DetailView` (3 sayfa stack koordinatörü) | `ui/views/detail_view.py` |

### UI Katmanları (2026-07-03 itibariyle — "Tüm Kaynaklar" sayfası kaldırıldı)

```
MainWindow (ince compose, ~55 satır)
├── Sidebar
├── ContentWorkspace
│     ├── SettingsView (kategori/etiket CRUD)
│     └── UrlShowcaseView (tek içerik sayfası — 2 iç görünüm modu, bkz. [[url_vitrin]])
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

`_STATIC_ITEMS` ile tanımlı 2 nav öğesi (2026-07-03'te "Tüm Kaynaklar" kaldırıldı — bkz. [[url_vitrin]]):

| Etiket | Filter Key | Yönlendirme |
|--------|-----------|-------------|
| Bağlantı Vitrini | `"url_showcase"` | UrlShowcaseView — ana sayfa |
| Ayarlar | `"settings"` | SettingsView — kategori/etiket CRUD |

`"inbox"/"planned"/"favorites"` gibi durum bazlı filtreler artık ayrı bir nav öğesi değil — `FilterBar`'ın Durum chip'leri ve Favoriler chip'i üzerinden (hangi sayfada olursa olsun) uygulanır.

Alt kısımda iki `ToggleSwitch` satırı: **Tema Değiştir** ve **Sade Mod**. Sidebar `event_bus.sidebar_filter_changed(filter_key)` yayınlar; `ResourceFlow._on_filter_changed` yakalar → `ContentWorkspace.apply_filter()`. "Sade Mod" toggle'ı `event_bus.simple_mode_toggled(bool)` yayınlar (bkz. [[event_bus]]) — **UrlShowcaseView'ın hangi iç görünümü gösterdiğini değiştirir** (detay: [[url_vitrin]]), kalıcılık yok, oturum içinde bellekte tutulur (tema toggle'ıyla aynı davranış). `set_collapsed()` daraltılmış sidebar'da her iki toggle etiketini de gizler.

---

## Orta — `ContentWorkspace` (QStackedWidget)

`MainWindow._build_ui` içinde `QSplitter`'ın sol widget'ı. İki sayfa (2026-07-03'te `ContentView` kaldırıldı, bkz. [[url_vitrin]]):

| Index | Widget | Ne zaman gösterilir |
|-------|--------|---------------------|
| 0 | `SettingsView` | `"settings"` filtresi |
| 1 | `UrlShowcaseView` | Her şey (tek içerik sayfası) |

### SettingsView (`ui/views/settings_view.py`)
`QTabWidget`, iki sekme:
- **Kategoriler:** Chip/grid izgara (`CategoryRow`, `FlowLayout` ile sarmalanır) + alt kısımda inline ekleme formu (ad/renk/ikon). Renk seçimi `ColorPickerButton` ile interaktif yapılır.
- **Etiketler:** Chip/grid izgara (`TagRow`) + inline ekleme formu (ad)

Her `CategoryRow` / `TagRow`: inline düzenle + 2-tıklı sil. `QDialog/QMessageBox` kullanılmaz. Edit moduna geçişte (veya sil-onay metni değişince) satırın genişliği değiştiği için `self.updateGeometry()` çağrılır — bu, sarmalayan `FlowLayout`'a yeniden diziliş yapması gerektiğini bildirir (Qt bunu custom layout'larda otomatik yapmaz).

Düzenle/Sil aksiyonları metin buton yerine `ui/components/icon_action_button.py::IconActionButton` (26x26, `QtAwesomeIcons.EDIT`/`DELETE`, tema-duyarli) kullanir — `card_icon_button.py::_CardIconButton` deseniyle tutarli ama toggle degil sabit-aksiyon butonu. `set_state(icon, color_role, tooltip, object_name)` ile sil-onay durumuna gecilir (ikon ayni kalir, renk `DANGER` → `DANGER_HOVER`, tooltip "Silmek için tekrar tıkla" olur, objectName QSS'in `#RowDeleteConfirmButton` kuralini tetikler). Edit moduna girildiginde sil-onay durumu otomatik sifirlanir (`_reset_delete_button()`) — önceden bu sifirlama sadece `_confirm_pending` bayragini guncelliyor, buton metnini guncellemiyordu (kucuk bir tutarlilik hatasi, bu turda giderildi).

**Ortak yardımcı — `ui/components/flow_layout.py::build_flow_stack()`:** Boş-durum etiketi + kaydırılabilir `FlowLayout` izgarası içeren bir `QStackedWidget` kurar (`GRID_PAGE`/`EMPTY_PAGE` sabitleri). Hem `UrlShowcaseView` (rich/simple kart modları) hem `SettingsView` (kategori/etiket grid'i) bu fonksiyonu kullanır — önceden `UrlShowcaseView` içinde özel/private bir fonksiyondu, DRY için ortak bileşene taşındı (2026-07-04).

### UrlShowcaseView (`ui/views/url_showcase_view.py`) — tek içerik sayfası
Detaylı açıklama: [[url_vitrin]]. Özet: **Üst Bar:** `SearchBar` + "Yeni Ekle" butonu — **FilterBar** (`ui/components/filter_bar.py`, "yükseltilmiş navbar kartı" tasarımı, bkz. altındaki not) — **InlineBanner** — içerik alanı `_mode_stack` (`QStackedWidget`, 2 mod): "rich" (varsayılan, `UrlRichCard` + url-only) / "simple" ("Sade Mod" açık, `ResourceCard` + tüm kaynaklar).

**FilterBar görsel tasarımı (2026-07-02):** Gövdeden ayrık "yükseltilmiş navbar kartı" — kendi arka planı (`surface_elevated`), kenarlığı, 12px yuvarlak köşesi ve `QGraphicsDropShadowEffect` gölgesi var (`Colors.SHADOW`, tema değişince güncellenir). `QFrame` alt sınıfı olduğu için QSS `background-color`/`border-radius`'un boyanması `WA_StyledBackground` attribute'una bağlı — bu attribute set edilmeden QSS arka planı yoksayılır (Qt gotcha'sı). Filtre grupları arası ince `#FilterSeparator` ayraçlarla görsel olarak bölünür. "Temizle" butonu hiçbir filtre aktif değilken otomatik devre dışı kalır (`_update_clear_button_state()`). `%RRGGBBAA` (CSS-stili, alfa sonda) tema renklerini Qt'nin beklediği `#AARRGGBB` formatına çeviren `ui/theme_utils.py::to_qcolor()` kullanılır.

**Kart üstü pin/favori:** `PinButton` + `FavoriteButton` (`ui/components/card_icon_button.py`). Tıklama event_bus üzerinden `ResourceFlow → controller.toggle_pin/toggle_favorite`. Pinli kayıt her sorguda en üste gelir.

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

`ResourceFlow._on_form_submitted` ayrımı yapar → `controller.add_resource` veya `controller.update_resource`. **Performans notu (2026-07-03):** bu iki controller çağrısı `event_bus.resource_added`/`resource_updated` yayınlar ve bu, `ResourceFlow._on_resource_changed` üzerinden zaten senkron olarak `workspace.refresh()`'i tetikler — `_on_form_submitted` eskiden ayrıca kendi `workspace.refresh()`'ini de çağırıyordu (gereksiz ikinci tam sorgu+kart-yeniden-kurulumu). Bu tekrar kaldırıldı; tek doğruluk kaynağı artık event bus.

---

## Kart Tipleri

| Tip | Dosya | Kullanım |
|-----|-------|----------|
| `ResourceCard` | `ui/components/resource_card.py` | UrlShowcaseView — "simple" mod (Sade Mod açık, tüm kaynaklar) |
| `UrlRichCard` | `ui/components/url_rich_card.py` | UrlShowcaseView — "rich" mod (varsayılan, url-only) |

Kartlar `AccentFrame` tabanlıdır: sol accent şeridi painter ile çizilir, hover durumunda kısa shadow/lift animasyonu alır. `ResourceCard` vurgu rengi kuralı: Kategori rengi > Durum rengi (fallback) şeklindedir. Durum/tag/kategori rozetleri `ColorBadge`, kategori renk önizlemeleri `ColorSwatch` ile çizilir. Her iki kart tipi de tam içerikle render edilir — `ResourceCard`'ın görsel detay gizleyen bir "sade" varyantı yoktur (bkz. [[url_vitrin]]'deki Sade Mod düzeltmesi).

---

## Boş Durum (Empty State)
Sonuç yokken `UrlShowcaseView`'in ilgili moduna ait iç `QStackedWidget`'ı boş-durum sayfasına geçer (`_rich_stack`/`_simple_stack`, her biri kendi `EmptyStateLabel`'ına sahip). `SettingsView`'daki kategori/etiket grid'leri de aynı `build_flow_stack()` deseniyle kendi boş-durum sayfasına sahiptir (`AppStrings.EMPTY_CATEGORIES_MSG`/`EMPTY_TAGS_MSG`).

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
