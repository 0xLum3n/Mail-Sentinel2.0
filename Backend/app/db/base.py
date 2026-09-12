"""SQLAlchemy declarative base for all PostgreSQL ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class inherited by every SQLAlchemy ORM model."""

    pass
