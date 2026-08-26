from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

if not database_exists(engine.url):
    create_database(engine.url)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
