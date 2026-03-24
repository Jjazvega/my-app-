from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.tenant import get_current_tenant_id


engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=settings.DEBUG and settings.ENVIRONMENT == "DEV",
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        session.info["tenant_id"] = get_current_tenant_id()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
