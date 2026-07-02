# Veritabanı Migrasyonları (Alembic)

Şema değişiklikleri artık [Alembic](https://alembic.sqlalchemy.org/) ile versiyonlanır. Eskiden `utils/db_utils.py` içinde `Base.metadata.create_all()` + elle yazılmış `_LIGHTWEIGHT_MIGRATIONS` listesi (tek satır `ALTER TABLE`) kullanılıyordu; bu mekanizma kolon silme/tip değiştirme gibi senaryoları desteklemiyordu ve yeni her değişiklik için elle liste güncellemesi gerektiriyordu.

## Dosya Yerleşimi

- `pkm_app/alembic.ini` — Alembic konfigürasyonu.
- `pkm_app/migrations/env.py` — modelleri import edip `Base.metadata`'yı `target_metadata` yapar, DB URL'ini `core.config.settings.DATABASE_URL`'den okur (alembic.ini'deki placeholder ezilir).
- `pkm_app/migrations/versions/` — revizyon dosyaları. İlk revizyon (`..._baseline.py`) mevcut 7 tabloyu (`categories`, `tags`, `resources`, `resource_tags_link`, `highlights`, `vocabulary`, `ideas`) `alembic revision --autogenerate` ile üretildi. İkinci revizyon (`..._ideas_tablosunu_kaldir.py`), Fikirler modülü kaldırılırken `ideas` tablosunu drop eder.

## `init_db()` Akışı (`utils/db_utils.py`)

Üç senaryo ayırt edilir (`inspect(engine).get_table_names()` ile):

1. **Sıfırdan kurulum** (hiç tablo yok): `alembic upgrade head` migration zincirini baştan çalıştırır, tüm tabloları oluşturur.
2. **Alembic-öncesi (legacy) veritabanı** (tablolar var ama `alembic_version` yok — örn. bu değişiklikten önce oluşturulmuş bir kullanıcı DB'si): şemaya dokunmadan `alembic stamp head` ile mevcut durum "head" olarak işaretlenir. Kullanıcı verisi korunur, `CREATE TABLE` çakışması olmaz.
3. **Zaten Alembic ile yönetilen DB**: sadece bekleyen migration'lar (varsa) uygulanır.

`_apply_lightweight_migrations()` (eski mekanizma) hâlâ `init_db()`'nin başında çalışır — çok eski bir DB dosyasında `is_favorite` kolonu bile yoksa önce onu ekler, sonra Alembic akışı devreye girer. Yeni şema değişiklikleri için bu listeye eklenme yapılmaz; bunun yerine yeni bir Alembic revizyonu oluşturulur.

## Yeni Migration Ekleme

```bash
cd pkm_app
alembic revision --autogenerate -m "kisa_aciklama"
# uretilen dosyayi migrations/versions/ altinda incele, gerekirse elle duzelt
```

`env.py` zaten `Base.metadata`'yı okuduğu için modelde yapılan değişiklik otomatik algılanır. Üretilen dosya mutlaka gözden geçirilmeli (autogenerate her zaman doğru `downgrade()` üretmeyebilir, index/constraint isimlendirmesi bazen elle düzeltme ister).

## Doğrulama Notu

Bu geçiş, gerçek kullanıcı veritabanının (`%APPDATA%/PKM/pkm_app.db`) bir **kopyası** üzerinde test edildi: legacy senaryoda tüm satırlar (resources, categories, tags, ideas) değişmeden korundu, `alembic_version` doğru eklendi, ikinci `init_db()` çağrısı idempotent çalıştı. Orijinal dosyaya dokunulmadı (MD5 doğrulandı).

## ⚠️ Tuzak: `env.py` her zaman `settings.DATABASE_URL`'i kullanır

`migrations/env.py:36` — `config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)` — bu satır, `alembic_command.upgrade(cfg, ...)` çağrısına **hangi `AlembicConfig` nesnesi verilirse verilsin**, env.py import edildiği an URL'i `core.config.settings.DATABASE_URL` (gerçek prod DB yolu) ile ezer. Bir migration'ı bir **kopya** DB üzerinde test etmek için `cfg.set_main_option("sqlalchemy.url", ...)` YETMEZ — `core.config.settings.DATABASE_URL`'in kendisini (örn. `monkeypatch.setattr(db_utils.settings, "DATABASE_URL", kopya_url)` ile, bkz. `tests/test_repositories/test_db_utils.py`) geçici olarak değiştirmek gerekir. Aksi halde migration sessizce gerçek veritabanına uygulanır.
