"""
Script to initialize database and create initial migration.
Используется только для локальной разработки.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.db.database import init_db, close_db
import structlog

logger = structlog.get_logger()


async def main():
    """Initialize database."""
    try:
        logger.info("initializing_database")
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        raise
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())



