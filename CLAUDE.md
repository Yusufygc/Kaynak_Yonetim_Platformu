# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

- **Conda env:** `C:\Users\ysfygc\anaconda3\envs\KaynakYonetim`
- **Activate:** `conda activate KaynakYonetim`
- **Run app:** `python pkm_app/main.py`
- **Install deps:** `pip install -r requirements.txt`
- **Run tests:** `pytest pkm_app/tests/`
- **Single test:** `pytest pkm_app/tests/test_services/test_resource_service.py::TestClassName::test_method`

## Wiki (Read First)

Before any code change, read `docs/wiki/index.md`. It maps every architectural decision. Follow links to relevant pages rather than re-deriving from scratch.

Operasyon komutları: `[INGEST]` yeni kaynak al → wiki güncelle, `[QUERY]` wiki üzerinden cevapla, `[LINT]` wiki sağlık kontrolü.

## Architecture

Three-layer separation — UI never touches the database directly:

```
UI (PySide6 views/components)
  └── Controllers  →  Services (business logic, validation, commit/rollback)
                          └── Repositories (SQLAlchemy queries only, no business logic)
                                  └── Models (SQLAlchemy declarative, models/ dir)
```

**Event Bus** (`core/events.py`) — Singleton `_EventBus(QObject)`. UI components never reference each other directly; all state changes flow through `event_bus.signal.emit()` / `.connect()`. Add new signals here when needed.

**Theme Manager** (`core/theme_manager.py`) — Singleton. QSS files use `{{ variable }}` placeholders; ThemeManager fills them from `core/themes/dark.py` / `light.py` dicts and calls `QApplication.setStyleSheet()`. Emits `event_bus.theme_changed` so components re-render qtawesome icons.

**Session ownership:** `commit()` and `rollback()` belong in the Service layer, never in Repositories.

## Hard Rules

**Code principles:**
- **SOLID:** Every class has single responsibility. Open/Closed: extend, don't modify. Use ABCs for Dependency Inversion.
- **DRY:** No repeated logic. Common functions go to `utils/` or `helpers/`.
- **No hacks:** "Works for now" shortcuts are forbidden. Every module must be testable and isolated when written.

**Styling:**
- No inline `setStyleSheet`. All styles live in `assets/styles/*.qss`.
- Each major window or component gets its own `.qss` file (e.g. `main_window.qss`, `resource_card.qss`).
- Colors are read from `core/constants/colors.py` and dynamically formatted (string interpolation) into QSS before applying — never hardcoded HEX values in `.qss` files.

**Assets:**
- No hard-coded colors, fonts, or strings. Source from `core/constants/colors.py`, `fonts.py`, `strings.py`.
- Standard icons: `qtawesome`. Custom icons/logos: SVG in `assets/icons/`, referenced via `core/constants/icons.py`.

**Error & observability:**
- No `print()`. Use `core/logger.py` (logs to console + `app.log`).
- Raise project-specific exceptions from `core/exceptions.py` (`InvalidURLError`, `ResourceNotFoundError`, `ValidationError`, `DuplicateRecordError`) — not bare `Exception`.

**Config & DI:**
- Config via `core/config.py` (Pydantic `BaseSettings` or `os.environ`). No hardcoded paths.
- Session and dependencies passed through `__init__`, not created inside classes.

## Wiki Güncellemesi

Her kod değişikliği, yeni modül, kütüphane ekleme veya mimari karar sonrasında:
1. İlgili `docs/wiki/*.md` sayfasını güncelle.
2. `docs/wiki/log.md` dosyasının **en üstüne** giriş ekle: `## [YYYY-AA-GG] [İŞLEM_TİPİ] | Kısa açıklama`
3. Yeni sayfa açıldıysa `docs/wiki/index.md`'ye de ekle.

## Commit Kuralları

- Commit mesajları **Türkçe** yazılır. Türkçe karakterlere dikkat et (ş, ğ, ü, ö, ı, ç).
- Başlık ≤ 50 karakter, açıklayıcı ve işlemin "neden" yapıldığını anlatan gövde.
- Commit mesajlarında "Claude Code" veya herhangi bir AI aracı referansı **verilmez**.

## Key Files

| Purpose | Path |
|---------|------|
| Entry point | `pkm_app/main.py` |
| Event Bus | `core/events.py` |
| Theme Manager | `core/theme_manager.py` |
| Custom exceptions | `core/exceptions.py` |
| DB session/utils | `utils/db_utils.py` |
| Generic CRUD | `repositories/base_repository.py` |
| Main resource queries | `repositories/resource_repo.py` |
| Core business logic | `services/resource_service.py` |

## Database

SQLite + SQLAlchemy 2.0 declarative. Main tables: `resources` (has `extra_metadata JSON` for type-specific data), `categories`, `tags`, `resource_tags_link` (N:N). Future tables already in schema: `highlights`, `vocabulary`. All datetimes UTC via `default=func.now()`.
