from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dto import LoginRequest, MeResponse, RegisterRequest, TokenResponse
from app.application.use_cases import AuthUseCases
from app.core.database import get_db
from app.core.security import get_token_payload
from app.core.tenant import get_tenant_id
from app.infrastructure.user_repository import UserRepository


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    payload: RegisterRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    use_cases = AuthUseCases(UserRepository(db))
    token = await use_cases.register(payload.email, payload.password, tenant_id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    use_cases = AuthUseCases(UserRepository(db))
    token = await use_cases.login(payload.email, payload.password, tenant_id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
async def me(
    token_payload: dict = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    use_cases = AuthUseCases(UserRepository(db))
    user = await use_cases.me(
        user_id=int(token_payload["sub"]),
        tenant_id=token_payload["tid"],
    )
    return MeResponse(id=user.id, email=user.email, tenant_id=user.tenant_id)
