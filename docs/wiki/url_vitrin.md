# URL Vitrini ve Görsel Kart Sistemi

**Kaynak (Raw Source):** `url_vitrin_layout.md` (kök dizin)

## Modülün Amacı
Web bağlantılarını (URL) metin listesinde kaybetmemek için OpenGraph/meta verilerinden beslenen zengin "Görsel Kartlar" oluşturulur ve "Bağlantı Vitrini" sekmesinde sergilenir.

## Bileşenler

### URL Vitrin Sekmesi — `ui/views/url_showcase_view.py`
- **Uygulamanın açılış (varsayılan) sayfasıdır.** `main_window.py` başlangıçta `self._sidebar.select_by_key("url_showcase")` + `self._workspace.apply_filter("url_showcase")` çağırır; sidebar'da da "Bağlantı Vitrini" seçili görünür.
- `ContentWorkspace._stack` içinde `_PAGE_URL_SHOWCASE = 2` olarak mount edilmiştir.
- Sidebar tıklamasıyla da açılır: `Sidebar` → `event_bus.sidebar_filter_changed("url_showcase")` → `ResourceFlow._on_filter_changed` → `ContentWorkspace.apply_filter("url_showcase")` → `_show_url_showcase()` → `view.load_resources(resources)`.
- **Layout:** `FlowLayout` içinde `QScrollArea` (h_spacing=16, v_spacing=16).
- Sadece `url` alanı dolu kaynaklar listelenir (`urls_only` filtresi).

### Zengin URL Kartı — `ui/components/url_rich_card.py`
`QFrame` veya `QWidget` tabanlı, standart `resource_card.py`'dan büyük ve görsel odaklı.

**İç Yapı (yukarıdan aşağıya):**
1. **Kapak Görseli:** Yuvarlatılmış köşeli thumbnail. Yoksa: sitenin favicon'u veya kategorinin büyük+soluk ikonu.
2. **Başlık + Özet:** Meta title (bold, max 2 satır) + meta description (gri, elips).
3. **Alt Bar:** Kategori/etiket rozeti (sol) · "Tarayıcıda Aç" butonu (sağ).

## Görsel Dinamikler
- **Dinamik Çerçeve:** `border-left: 4px solid {kategori/etiket rengi}` — renk kullanıcıya konu kodlaması sunar (Mavi=Yazılım, Yeşil=Finans…).
- **Hover Efekti:** Kartın hafif yukarı kalkması veya DropShadow belirginleşmesi (QSS).
- **Thumbnail:** `extra_metadata.thumbnail` varsa `UrlRichCard` Qt network ile async yükler; hata veya metadata yoksa placeholder ikon kalır.

## Metadata Akışı
- URL'li kaynak eklendiğinde/güncellendiğinde tarama **arka planda** çalışır (`ResourceFlow._schedule_scrape` → `QThreadPool`), UI thread'i bloklamaz. Sonuç `extra_metadata` olarak DB'ye yazılınca `_on_scrape_finished` kaynağı günceller.
- Çıkarılan alanlar: `og_title`, `og_description`, `thumbnail`, `favicon`.
- Request/parse hataları kaynak kaydını engellemez; boş metadata ile devam edilir. Tarama sırasında beklenmeyen bir istisna olursa `_ScrapeWorker` artık bunu yutmaz — `log.exception(...)` ile loglanır, worker çökmez.

## Bilinen Hata Düzeltmesi: Sayfa Geçişinde Donma

`ContentWorkspace.apply_filter()` her sayfa geçişinde iki `FilterBar.clear()` çağırıyordu; `clear()` sonunda her zaman `filters_changed` sinyalini senkron fırlattığı için `refresh()` **henüz güncellenmemiş eski sayfa index'iyle** tetikleniyordu. Vitrin sayfasından ayrılırken bu, `_show_url_showcase()`'in (tüm kartların yok edilip yeniden kurulması + her biri için yeni ağ isteği) gereksiz yere 2 kez fazladan çalışmasına, dolayısıyla donmaya yol açıyordu. Çözüm: `FilterBar.clear(notify=False)` — `apply_filter()` zaten hemen ardından doğru sayfayı tek seferde yüklediği için ara `refresh()` tetiklemesine gerek yok. Ayrıca `UrlRichCard._on_thumbnail_loaded()` artık ağ/decode hatalarını `log.warning(...)` ile loglar (önceden sessizce yutuluyordu).

## Etkileşim
| Aksiyon | Sonuç |
|---------|-------|
| "Tarayıcıda Aç" butonuna tıkla | `QDesktopServices.openUrl(QUrl(url))` — işletim sisteminin varsayılan tarayıcısı |
| Kartın gövdesine / görseline tıkla | `event_bus.resource_selected.emit(id)` → sağ detay paneli açılır |

## İlgili Sayfalar
[[ui_layout]] · [[event_bus]] · [[veritabani_semasi]] · [[core_servisler]]
