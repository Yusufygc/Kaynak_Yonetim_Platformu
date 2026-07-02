# Event Bus (Sinyal ve Olay Yönetimi)

## Mimari
- **Desen:** Singleton + Observer (`QObject` üzerinden)
- **Dosya:** `core/events.py`
- UI bileşenleri birbirini **doğrudan referans almaz** — her durum değişikliği merkezi bus üzerinden iletilir.

---

## Tanımlı Sinyaller

### Kaynak Sinyalleri
| Sinyal | Tip | Tetiklenme |
|--------|-----|-----------|
| `resource_added` | `Signal(int)` | Yeni kaynak eklendi — id taşır |
| `resource_updated` | `Signal(int)` | Kaynak güncellendi — id taşır |
| `resource_deleted` | `Signal(int)` | Kaynak silindi — id taşır |
| `resource_selected` | `Signal(int)` | Karta tıklandı → sağ panel açılır |

### Kategori Sinyalleri
| Sinyal | Tip | Tetiklenme |
|--------|-----|-----------|
| `category_added` | `Signal(int)` | Yeni kategori — id taşır |
| `category_updated` | `Signal(int)` | Kategori güncellendi |
| `category_deleted` | `Signal(int)` | Kategori silindi |

### Etiket Sinyalleri
| Sinyal | Tip | Tetiklenme |
|--------|-----|-----------|
| `tag_added` | `Signal(int)` | Yeni etiket — id taşır |
| `tag_updated` | `Signal(int)` | Etiket güncellendi |
| `tag_deleted` | `Signal(int)` | Etiket silindi |

### UI / Navigasyon Sinyalleri
| Sinyal | Tip | Tetiklenme |
|--------|-----|-----------|
| `sidebar_filter_changed` | `Signal(str)` | Nav item seçildi veya arama yapıldı. Değer: `"all"`, `"inbox"`, `"planned"`, `"favorites"`, `"url_showcase"`, `"settings"`, `"search:<keyword>"`, `"category:<id>"` |
| `search_query_changed` | `Signal(str)` | SearchBar metnin değişti → `MainController._on_search` yönlendirir |
| `resource_pin_toggle_requested` | `Signal(int)` | Kart pin ikonu tıklandı → `ResourceFlow → controller.toggle_pin` |
| `resource_favorite_toggle_requested` | `Signal(int)` | Kart yıldız ikonu tıklandı → `ResourceFlow → controller.toggle_favorite` |
| `filters_changed` | `Signal(dict)` | FilterBar değişti (ContentWorkspace tarafından kullanılır; view sinyalleri üzerinden lokal de geçer) |
| `error_occurred` | `Signal(str)` | Herhangi bir işlem hatası — ContentView / SettingsView banner gösterir |
| `theme_changed` | `Signal(dict)` | Tema değişti → bkz. [[tema_yonetimi]] |

---

## Kullanım Kuralları
- **Emit:** Controller, servis işlemi başarılı olduktan **hemen sonra** sinyal fırlatır.
- **Connect:** View / bileşen `__init__` içinde bus'a abone olur.
- **Bellek:** Bileşen yok edilirken `disconnect()` çağrılmalı veya PySide6 parent-child yaşam döngüsüne güvenilmeli.
- **error_occurred:** Controller `try/except` bloklarında hata → `event_bus.error_occurred.emit(str(exc))`. Banner bileşeni (InlineBanner) bunu yakalar.

---

## Örnek Kullanım

```python
# Emit (Controller tarafında)
event_bus.resource_updated.emit(resource.id)

# Connect (View tarafında)
event_bus.resource_updated.connect(self._reload)

# Hata yayını
event_bus.error_occurred.emit("Kaynak bulunamadı.")
```

## İlgili Sayfalar
[[tema_yonetimi]] · [[core_servisler]] · [[ui_layout]] · [[mimari_kurallari]]
