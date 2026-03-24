from fastapi import HTTPException, status

from app.core.security import create_access_token, hash_password, verify_password
from app.infrastructure.user_repository import UserRepository


class AuthUseCases:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def register(self, email: str, password: str, tenant_id: str) -> str:
        existing_user = await self.user_repository.get_by_email(
            email=email,
            tenant_id=tenant_id,
        )
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El email ya está registrado.",
            )

        hashed_password = hash_password(password)
        created_user = await self.user_repository.create(
            email=email,
            tenant_id=tenant_id,
            hashed_password=hashed_password,
        )
        return create_access_token(subject=str(created_user.id), tenant_id=tenant_id)

    async def login(self, email: str, password: str, tenant_id: str) -> str:
        user = await self.user_repository.get_by_email(email=email, tenant_id=tenant_id)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas.",
            )

        return create_access_token(subject=str(user.id), tenant_id=tenant_id)

    async def me(self, user_id: int, tenant_id: str):
        user = await self.user_repository.get_by_id(
            user_id=user_id,
            tenant_id=tenant_id,
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        return user
