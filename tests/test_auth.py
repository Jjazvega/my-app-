import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.security import decode_access_token, verify_password
from app.infrastructure.user_repository import UserModel


def test_register_stores_hashed_password_and_tenant(
    client,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "ana@example.com", "password": "supersecreta123"},
        headers={"X-Tenant-Id": "acme"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

    async def get_user() -> UserModel | None:
        async with session_factory() as session:
            result = await session.execute(
                select(UserModel).where(
                    UserModel.email == "ana@example.com",
                    UserModel.tenant_id == "acme",
                )
            )
            return result.scalar_one_or_none()

    user = asyncio.run(get_user())

    assert user is not None
    assert user.tenant_id == "acme"
    assert user.hashed_password != "supersecreta123"
    assert verify_password("supersecreta123", user.hashed_password)


def test_login_returns_valid_jwt(
    client,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    client.post(
        "/auth/register",
        json={"email": "luis@example.com", "password": "supersecreta123"},
        headers={"X-Tenant-Id": "globex"},
    )

    login_response = client.post(
        "/auth/login",
        json={"email": "luis@example.com", "password": "supersecreta123"},
        headers={"X-Tenant-Id": "globex"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    payload = decode_access_token(token)

    async def get_user() -> UserModel | None:
        async with session_factory() as session:
            result = await session.execute(
                select(UserModel).where(
                    UserModel.email == "luis@example.com",
                    UserModel.tenant_id == "globex",
                )
            )
            return result.scalar_one_or_none()

    user = asyncio.run(get_user())

    assert user is not None
    assert payload["sub"] == str(user.id)
    assert payload["tenant_id"] == "globex"
    assert payload["tid"] == "globex"
    assert payload["type"] == "access"


def test_me_returns_user_from_generated_token_and_ignores_spoofed_tenant_header(client) -> None:
    register_response = client.post(
        "/auth/register",
        json={"email": "maria@example.com", "password": "supersecreta123"},
        headers={"X-Tenant-Id": "initech"},
    )
    token = register_response.json()["access_token"]

    me_response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Tenant-Id": "tenant-malicioso",
        },
    )

    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["email"] == "maria@example.com"
    assert payload["tenant_id"] == "initech"
    assert isinstance(payload["id"], int)
