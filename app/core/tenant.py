from contextvars import ContextVar

from fastapi import Header

from app.core.config import settings


tenant_context: ContextVar[str] = ContextVar(
    "tenant_id",
    default=settings.DEFAULT_TENANT_ID,
)


def set_tenant_context(tenant_id: str) -> str:
    normalized_tenant_id = tenant_id.strip().lower()
    if not normalized_tenant_id:
        normalized_tenant_id = settings.DEFAULT_TENANT_ID
    tenant_context.set(normalized_tenant_id)
    return normalized_tenant_id


def get_current_tenant_id() -> str:
    return tenant_context.get()


async def get_tenant_id(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> str:
    return set_tenant_context(x_tenant_id or settings.DEFAULT_TENANT_ID)
