# database_config.py
import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("ASYNC_PG_CONN_STR")
if not DATABASE_URL:
    logger.error("ASYNC_PG_CONN_STR environment variable not set.")
    raise ValueError("ASYNC_PG_CONN_STR environment variable not set.")

engine = create_async_engine(
    DATABASE_URL,
    echo=False,   
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for all ORM models
Base = declarative_base()

async def init_db():
    """Initializes the database, creates schema and tables."""
    try:
        # Create schema if it doesn't exist
        async with engine.connect() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS aux"))
            await conn.commit()
            logger.info("Schema 'aux' ensured.")

        # Create all tables defined by Base subclasses
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ensured.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        raise

async def get_db_session() -> AsyncSession:
    """Dependency to get a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()