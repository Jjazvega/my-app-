# FastAPI Auth Base

Base de autenticación con FastAPI, PostgreSQL async, JWT y soporte multi-tenant.

## Instalación

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

Crea `.env` a partir de `.env.example`.

## Ejecución

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /health`

## Multi-tenant

Usa el header `X-Tenant-Id`. Si no se envía, usa `DEFAULT_TENANT_ID`.

## Docs

`http://127.0.0.1:8000/docs`
