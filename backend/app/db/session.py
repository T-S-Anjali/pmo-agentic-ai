"""Database session and initialization."""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Create tables on startup (dev only; use Alembic in prod)."""
    from app.db.models import Base  # noqa: F401
    import structlog
    logger = structlog.get_logger(__name__)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise e


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
