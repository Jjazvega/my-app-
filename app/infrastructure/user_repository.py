from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.user import User


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str, tenant_id: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email,
            UserModel.tenant_id == tenant_id,
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return User(
            id=row.id,
            email=row.email,
            tenant_id=row.tenant_id,
            hashed_password=row.hashed_password,
            created_at=row.created_at,
        )

    async def get_by_id(self, user_id: int, tenant_id: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.tenant_id == tenant_id,
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return User(
            id=row.id,
            email=row.email,
            tenant_id=row.tenant_id,
            hashed_password=row.hashed_password,
            created_at=row.created_at,
        )

    async def create(self, email: str, tenant_id: str, hashed_password: str) -> User:
        user = UserModel(
            email=email,
            tenant_id=tenant_id,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
        except Exception:
            await self.db.rollback()
            raise

        return User(
            id=user.id,
            email=user.email,
            tenant_id=user.tenant_id,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )
