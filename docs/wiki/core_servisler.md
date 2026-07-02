# Core Servisler ve Repository Katmanı

## Oturum (Session) Yönetimi
- `Session` sınıf içinde **yaratılmaz**; `__init__` üzerinden **enjekte edilir** (test edilebilirlik).
- `commit()` / `rollback()` → **Service katmanı** sorumluluğu.
- Repository sadece `session.add()` / `session.flush()` yapar, transaction yönetmez.

---

## Repository Katmanı (`repositories/`)

### BaseRepository — `repositories/base_repository.py`
Python `TypeVar` + `Generic` ile tüm modellere hizmet veren CRUD sınıfı.

| Metod | İmza |
|-------|------|
| `get_by_id` | `(id: int) -> Model \| None` |
| `get_all` | `() -> list[Model]` |
| `create` | `(obj: Model) -> Model` (flush, commit yok) |
| `update` | `(obj: Model) -> Model` (flush, commit yok) |
| `delete` | `(id: int) -> bool` |

### ResourceRepository — `repositories/resource_repo.py`

| Metod | Açıklama |
|-------|----------|
| `get_by_status(status: ResourceStatus)` | Duruma göre filtrele (inbox/planned/in_progress/completed) |
| `search_by_keyword(keyword: str)` | Başlık/URL/içerik — ILIKE |
| `get_with_tags(tag_ids: list[int])` | Etikete göre filtrele (N:N join) |
| `get_by_category(category_id: int)` | Kategoriye göre filtrele |
| `get_pinned()` | Sabitlenmiş kaynaklar |
| `get_urls_only()` | URL alanı dolu kaynaklar (Vitrin için) |

---

## Service Katmanı (`services/`)

### ResourceService — `services/resource_service.py`
**Bağımlılıklar:** `ResourceRepository`, `TagRepository`, `CategoryRepository`

| Metod | Kurallar |
|-------|----------|
| `get_all()` | Tüm kaynaklar |
| `get_by_id(id)` | Bulunamazsa `ResourceNotFoundError` |
| `get_by_status(status)` | `ResourceStatus` enum değeri alır |
| `search(keyword)` | `search_by_keyword` proxy |
| `get_by_category(id)` | Kategoriye göre |
| `get_urls_only()` | URL alanı dolu |
| `add_new_resource(data: dict)` | URL varsa regex doğrula (scheme zorunlu: `https?://`). Kategori ID varsa kontrol et. `tag_names` normalize + dedupe + get-or-create. `extra_metadata` verilmemişse URL metadata çekilir. `flush()` sonra `commit()`. Hata da `rollback()`. |
| `update_resource(id, data: dict)` | Sadece dict'te bulunan anahtarları günceller. URL validasyonu. `tag_names` varsa etiket ilişkilerini tam senkronize eder; boş liste tüm etiketleri kaldırır. `commit()`. |
| `update_resource_progress(id, progress)` | 0–100 dışı → `ValueError`. Progress=100 → status=COMPLETED. |
| `delete_resource(id)` | Bulunamazsa `ResourceNotFoundError`. Cascade ile etiket linkleri de silinir. |

**URL Validasyonu (`_validate_url`):** `^https?://` zorunlu — scheme'siz URL'ler reddedilir. Ayrı `_URL_RE` regex ile host+path doğrulanır.

### ScraperService — `services/scraper_service.py`

| Metod | Açıklama |
|-------|----------|
| `extract_metadata(url)` | `og_title`, `og_description`, `thumbnail`, `favicon` çıkarır. Request/parse hatasında log yazar ve `{}` döndürür. |

### TagService — `services/tag_service.py`

| Metod | Açıklama |
|-------|----------|
| `get_or_create_tag(name)` | Varsa getir, yoksa yarat + commit. Kaynak ekleme akışında kullanılır. |
| `create_tag(name)` | Kullanıcı niyetli — zaten varsa `DuplicateRecordError`. |
| `update_tag(id, new_name)` | Normalize, boşluk+duplicate kontrol, commit. |
| `delete_tag(id)` | Bulunamazsa `ResourceNotFoundError`. |
| `get_all()` | Tüm etiketler |

### CategoryService — `services/category_service.py`

| Metod | Açıklama |
|-------|----------|
| `create_category(name, color_hex, icon)` | HEX format doğrula (`#RRGGBB`). Duplicate → `DuplicateRecordError`. |
| `update_category(id, name, color_hex, icon)` | Aynı doğrulamalar. |
| `delete_category(id)` | İlişkili kaynakların `category_id` → NULL (SET NULL). |
| `get_all()` | Tüm kategoriler |
| `get_by_id(id)` | Tek kategori |

---

## Controller Katmanı (`ui/controllers/main_controller.py`)

UI ile service arasındaki köprü. Her method try/except ile sarılır; hata → `event_bus.error_occurred.emit(str(exc))`.

| Metod | Açıklama |
|-------|----------|
| `load_resources_by_filter(key)` | `"all"/"inbox"/"planned"/"url_showcase"/"category:N"` anahtarlarını service metodlarına yönlendirir |
| `search_resources(keyword)` | Boşsa `get_all()`, doluysa `search(keyword)` |
| `get_resource(id)` | Tek kaynak |
| `add_resource(data)` | `resource_added` emit |
| `update_resource(id, data)` | `resource_updated` emit |
| `update_progress(id, progress)` | progress güncelle |
| `delete_resource(id)` | `resource_deleted` emit |
| `load_categories()` / `load_tags()` | Tüm liste |
| `create/update/delete_category(...)` | `category_added/updated/deleted` emit |
| `create/update/delete_tag(...)` | `tag_added/updated/deleted` emit |

---

## Hata Sınıfları — `core/exceptions.py`

| Sınıf | Tetiklenme Koşulu |
|-------|------------------|
| `ValidationError` | Girdi kurallara uymadığında (boş ad, format hatası) |
| `ResourceNotFoundError` | ID'li kayıt bulunamadığında |
| `InvalidURLError` | URL formatı bozuk veya scheme eksik |
| `DuplicateRecordError` | Aynı isimde kategori/tag ekleme girişimi |

## İlgili Sayfalar
[[veritabani_semasi]] · [[dizin_yapisi]] · [[mimari_kurallari]] · [[event_bus]]
