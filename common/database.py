from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

BASEDIR = Path(__file__).parent.parent
DATABASE_URL = f"sqlite:///{(BASEDIR / 'bot_database.sqlite').resolve()}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()