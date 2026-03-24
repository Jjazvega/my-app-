from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    id: int | None
    email: str
    tenant_id: str
    hashed_password: str
    created_at: datetime | None = None
