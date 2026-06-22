from celery import Celery

from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker

from app.models import URL

import os

celery_app = Celery(
    "url_shortner",
    broker=os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    ),
    backend=os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0"
    )
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/urlshortner")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

@celery_app.task
def increment_click_count(short_code:str):
    db = SessionLocal()

    try:
        db.execute(
            update(URL)
            .where(URL.short_code == short_code)
            .values(
                click_count=URL.click_count + 1
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    

