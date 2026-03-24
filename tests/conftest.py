import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.routes_auth import router as auth_router
from app.core.database import get_db
from app.core.exceptions import register_exception_handlers
from app.core.tenant import get_current_tenant_id
from app.infrastructure.user_repository import Base


@pytest.fixture(scope="session")
def engine():
    test_engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async def setup() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup())
    yield test_engine

    async def teardown() -> None:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await test_engine.dispose()

    asyncio.run(teardown())


@pytest.fixture()
def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture()
def client(session_factory: async_sessionmaker[AsyncSession]) -> Generator[TestClient, None, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            session.info["tenant_id"] = get_current_tenant_id()
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def reset_db() -> None:
        async with session_factory() as session:
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            await session.commit()

    asyncio.run(reset_db())

    test_app = FastAPI(title="test-app")
    test_app.include_router(auth_router)
    register_exception_handlers(test_app)
    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()
