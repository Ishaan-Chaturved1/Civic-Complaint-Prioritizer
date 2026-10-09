import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

logger = logging.getLogger("civic.database")

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=False,
        future=True,
    )
    # Test connection
    with engine.connect() as conn:
        logger.info(f"Database connected using: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'local driver'}")
except Exception as e:
    logger.warning(f"Failed to connect to primary DB ({settings.DATABASE_URL}): {e}. Falling back to SQLite.")
    sqlite_url = "sqlite:///./civic_complaints.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        echo=False,
        future=True,
    )

# Enable foreign keys for SQLite
if engine.url.drivername.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
