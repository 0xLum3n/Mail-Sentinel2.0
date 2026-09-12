"""Database infrastructure package.

This package intentionally avoids importing connection-dependent modules at import
 time so model and migration discovery do not require a live database driver.
"""

from app.db.base import Base

__all__ = ["Base"]
