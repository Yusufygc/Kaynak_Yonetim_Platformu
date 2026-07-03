# Veritabanı Şeması

**Kaynak (Raw Source):** `veritabani.md` (kök dizin)

## Teknoloji Yığını
- **DB:** SQLite
- **ORM:** SQLAlchemy 2.0 (declarative mapping)
- **Tarihler:** UTC `datetime`, `default=func.now()`

## Tablolar

### `categories`
| Alan | Tip | Not |
|------|-----|-----|
| id | Integer PK | |
| name | String | Unique, Required |
| color_hex | String | Örn: `#FF0000` |
| icon | String | qtawesome kodu veya emoji |

### `tags`
| Alan | Tip | Not |
|------|-----|-----|
| id | Integer PK | |
| name | String | Unique, Required, küçük harf+boşluksuz |

### `resources` (Ana Tablo)
| Alan | Tip | Not |
|------|-----|-----|
| id | Integer PK | |
| title | String | Required |
| url | String | Nullable, **indexed** (2026-07-03) |
| category_id | Integer FK | `categories.id`, **indexed** (2026-07-03) |
| status | Enum | `INBOX` / `PLANNED` / `IN_PROGRESS` / `COMPLETED`, **indexed** (2026-07-03) |
| priority | Integer | 1-2-3, default 2 |
| progress | Float | 0.0–100.0 |
| is_pinned | Boolean | default False — listede üste sabitler, **indexed** (2026-07-03) |
| is_favorite | Boolean | default False — "Favoriler" koleksiyonu, **indexed** (2026-07-03) |
| content | Text | Markdown formatında notlar |
| extra_metadata | JSON | **Esnek alan** — tip-özel veriler (süre, yıldız, yazar…) |
| created_at | DateTime | default now |
| updated_at | DateTime | default now, onupdate now |

**Kategori silme:** `resources.category_id` FK davranışı `ON DELETE SET NULL` olarak kalır. ORM tarafında category->resources ilişkisinde `delete-orphan` yoktur; kategori silinince kaynak kaydı korunur.

**İndexler (migration `ff016ad9bf6e`):** `query_filtered` (bkz. [[core_servisler]]) tam olarak `status`/`category_id`/`is_favorite`/`is_pinned`/`url` kolonlarında filtreliyor ve sıralıyor; önceden sadece PK indeksliydi (full-table-scan riski). Bkz. [[veritabani_migrasyonlari]].

### `resource_tags_link` (N:N)
| Alan | Tip |
|------|-----|
| resource_id | FK → resources.id |
| tag_id | FK → tags.id |

### `highlights` (Vurgular — Gelecek Faz)
| Alan | Tip | Not |
|------|-----|-----|
| id | Integer PK | |
| resource_id | FK | `resources.id` |
| content | Text | Required |
| page_number | Integer | Nullable (PDF) |
| color | String | Vurgu rengi |
| created_at | DateTime | |

### `vocabulary` (Kelime Dağarcığı — Gelecek Faz)
| Alan | Tip | Not |
|------|-----|-----|
| id | Integer PK | |
| resource_id | FK | `resources.id` |
| word | String | Required |
| translation | String | Required |
| context_sentence | Text | Nullable |
| mastery_level | Integer | 0–5, spaced repetition |
| created_at | DateTime | |

## Hafif Migration
`utils/db_utils.py:_apply_lightweight_migrations()` mevcut SQLite dosyalarına eksik kolonları ekler (idempotent). `init_db()` her başlangıçta önce bunu çağırır, sonra `Base.metadata.create_all` ile yeni tabloları oluşturur. Şu an listedeki tek migration: `resources.is_favorite` kolonu (2026-05-17).

## AI Görevi
SQLAlchemy modelleri `models/` dizini altında ayrı dosyalarda oluştur. İlişkileri `relationship()` + `back_populates` ile çift yönlü tanımla.

## İlgili Sayfalar
[[dizin_yapisi]] · [[core_servisler]] · [[mimari_kurallari]]
