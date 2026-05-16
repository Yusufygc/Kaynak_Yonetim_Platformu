from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

# Modellerin import edildiginden emin olun
import models.category  # noqa: F401
import models.tag  # noqa: F401
import models.resource  # noqa: F401
import models.idea  # noqa: F401
from models.base import Base
from core.config import settings
from core.logger import log

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite icin gerekli
    echo=(settings.APP_ENV == "development"),
)


@event.listens_for(engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    if engine.url.get_backend_name() != "sqlite":
        return
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Mevcut SQLite tablolarinda eksik kolonlari ekleyen hafif migration listesi.
# (tablo_adi, kolon_adi, ALTER TABLE ifadesi)
_LIGHTWEIGHT_MIGRATIONS: list[tuple[str, str, str]] = [
    (
        "resources",
        "is_favorite",
        "ALTER TABLE resources ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT 0",
    ),
]


def _apply_lightweight_migrations(target: Engine) -> None:
    """Eski DB dosyalarinda eksik kolonlari ekler. Base.metadata.create_all
    yalnizca eksik *tablolari* olusturur, kolon ekleme yapmaz; bu yardimci
    onu tamamlar. Idempotent: kolon zaten varsa atlanir.
    """
    inspector = inspect(target)
    existing_tables = set(inspector.get_table_names())
    for table_name, column_name, ddl in _LIGHTWEIGHT_MIGRATIONS:
        if table_name not in existing_tables:
            continue
        cols = {col["name"] for col in inspector.get_columns(table_name)}
        if column_name in cols:
            continue
        with target.begin() as conn:
            conn.execute(text(ddl))
        log.info("Migration uygulandi: %s.%s eklendi", table_name, column_name)


def init_db() -> None:
    """Tüm tablolari olusturur. Uygulama baslarken bir kez cagrilir."""
    from models import Base  # dairesel import'tan kacmak icin
    _apply_lightweight_migrations(engine)
    Base.metadata.create_all(bind=engine)
    log.info("Veritabani tablolari olusturuldu/dogrulandi.")


def get_session() -> Session:
    """Yeni bir veritabani oturumu dondurur. Cagiran kapatmaktan sorumludur."""
    return SessionLocal()
