from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backtester.config import get_settings


class Base(DeclarativeBase):
    pass


database_url = get_settings().database_url
connect_args: dict[str, object] = {}
if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    if database_url.startswith("sqlite:///./"):
        Path("data").mkdir(exist_ok=True)

engine = create_engine(database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

