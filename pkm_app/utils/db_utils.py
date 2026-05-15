from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

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


def init_db() -> None:
    """Tüm tablolari olusturur. Uygulama baslarken bir kez cagrilir."""
    from models import Base  # dairesel import'tan kacmak icin
    Base.metadata.create_all(bind=engine)
    log.info("Veritabani tablolari olusturuldu/dogrulandi.")


def get_session() -> Session:
    """Yeni bir veritabani oturumu dondurur. Cagiran kapatmaktan sorumludur."""
    return SessionLocal()
