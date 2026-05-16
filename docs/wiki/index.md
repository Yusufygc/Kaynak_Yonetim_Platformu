# Wiki İçerik Haritası — PKM / Kaynak Yönetim Platformu

**Stack:** PySide6 · SQLAlchemy 2.0 · SQLite · qtawesome  
**Ortam:** `C:\Users\ysfygc\anaconda3\envs\KaynakYonetim`

---

## Kurallar ve Mimari

| Sayfa | Özet |
|-------|------|
| [[mimari_kurallari]] | SOLID, Clean Code, DRY, merkezi varlık yönetimi, katman kuralları |
| [[dizin_yapisi]] | Proje kök dizini, her modülün sorumluluğu, katman tablosu |

## Veritabanı

| Sayfa | Özet |
|-------|------|
| [[veritabani_semasi]] | Tüm tablolar (categories, tags, resources, highlights, vocabulary), alan tanımları |

## Servisler ve İş Mantığı

| Sayfa | Özet |
|-------|------|
| [[core_servisler]] | Repository/Service/Controller katmanları, ResourceService.update_resource, TagService CRUD, URL regex, custom exceptions |
| [[ideas_module]] | Bağımsız Kanban özellikli "Fikirler" modülü. Idea model, service ve UI bileşenleri. |

## Arayüz (UI)

| Sayfa | Özet |
|-------|------|
| [[ui_layout]] | Three-Pane mimari, main_stack (3 sayfa), Sidebar (5 nav item), kart tipleri, DetailView (görüntüle/form/sil/düzenle), boş durum |
| [[url_vitrin]] | URL Showcase sekmesi (main_stack index 2), UrlRichCard, MainWindow tetikler |

## Altyapı

| Sayfa | Özet |
|-------|------|
| [[event_bus]] | Singleton+Observer event sistemi, sinyaller, emit/connect kuralları |
| [[tema_yonetimi]] | Dinamik QSS enjeksiyonu, ThemeManager, Dark/Light toggle, qtawesome ikon güncelleme |

## Meta

| Sayfa | Özet |
|-------|------|
| [[log]] | Kronolojik değişiklik kayıt defteri |

---

## Operasyon Komutları (Anayasa)

| Komut | Ne yapar |
|-------|----------|
| `[INGEST]` | Yeni kaynak al → wiki sayfası oluştur → `index.md` + `log.md` güncelle |
| `[QUERY]` | `index.md` → ilgili sayfa → wiki bilgisiyle cevap ver |
| `[LINT]` | Çelişki, orphan sayfa, kırık link tara → rapor sun → onay sonrası düzelt |

**Kural:** Her sohbet başında `docs/wiki/index.md` okunur. Sıfırdan keşif yapılmaz; biriken bilgi kullanılır.
