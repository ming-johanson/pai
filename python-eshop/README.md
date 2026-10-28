# eShopOnWeb — Python Edition

A Vibe-coded Python rewrite of the eShopOnWeb storefront. Uses a clean architecture:

**Router → Service → Database Client → SQLite**

The React frontend talks to a FastAPI backend over JSON. Scope matches the original storefront: catalog, basket, auth, checkout, and orders — no admin, no payment gateway, no product detail page.

## Architecture

```
python-eshop/
├── backend/
│   ├── routers/      # HTTP layer (FastAPI APIRouter)
│   ├── services/     # Business logic
│   ├── db/           # DatabaseClient + schema + seed
│   └── models/       # Pydantic schemas + dataclasses
└── frontend/         # Vite + React + Tailwind SPA
```

| Python layer | Original C# project | Responsibility |
|---|---|---|
| `routers/` | `Web/` pages & controllers | HTTP, validation, auth headers |
| `services/` | `ApplicationCore/` | Basket merge, checkout rules |
| `db/client.py` | `Infrastructure/` | All SQL queries |
| SQLite file | SQL Server CatalogDb | Persistent storage |

## Prerequisites

- Python 3.11+ (tested with 3.14)
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) — required for the backend

## Quick start

Open two terminals.

### 1. Backend

```bash
cd python-eshop/backend
uv sync
uv run python run.py
```

- API: http://127.0.0.1:8765
- Swagger docs: http://127.0.0.1:8765/docs
- Static product images: http://127.0.0.1:8765/static/images/products/

### Running the tests

```bash
cd python-eshop/backend
uv run pytest
```

The suite boots the API in-process against a throwaway SQLite database, so it never touches your `eshop.db`, needs no running server and makes no network calls.

> **Note:** Do not use bare `uvicorn main:app --reload` — that defaults to port 8000, which may already be in use. Always use `uv run python run.py`.

### 2. Frontend

```bash
cd python-eshop/frontend
npm install
npm run dev
```

- App: http://127.0.0.1:4321

The Vite dev server proxies `/api` and `/static` to the backend.

## Seeded accounts

Nothing in the shop is public and there is no self-service registration: every
account is created by the organiser. The seed creates one of each role.

| Role | Email | Password |
|---|---|---|
| rep (demo sponsor rep) | `demouser@perthai.com.au` | `Pass@word1` |
| organiser | `organiser@perthai.com.au` | `Organise@1` |
| supplier | `supplier@perthai.com.au` | `Supply@1` |

Any signed-in user can change their password from the account page (click
your email in the header).

## Shopping flow

1. Sign in — every page redirects to the sign-in form until you do
2. Browse the catalog — filter by brand/type, paginate (10 items per page)
3. Add items to basket — the basket is kept on the server under your account
4. Checkout — review order, click **Pay now** (uses a hardcoded shipping address like the original)
5. View orders — **My Orders** in the header

## API overview

| Method | Route | Auth |
|---|---|---|
| GET | `/api/health` | Public |
| POST | `/api/auth/login` | Public |
| GET | `/api/auth/me` | JWT required |
| POST | `/api/auth/password` | JWT required |
| GET | `/api/catalog/items` | JWT required |
| GET | `/api/catalog/brands` | JWT required |
| GET | `/api/catalog/types` | JWT required |
| GET | `/api/basket` | JWT required |
| POST | `/api/basket/items` | JWT required |
| PUT | `/api/basket/items` | JWT required |
| POST | `/api/orders` | JWT required |
| GET | `/api/orders` | JWT required |
| GET | `/api/orders/{id}` | JWT required |
| POST | `/api/organiser/users` | JWT, organiser role |

A JWT for the wrong role gets a 403; a missing, expired or tampered token gets
a 401 and never falls back to anonymous access.
