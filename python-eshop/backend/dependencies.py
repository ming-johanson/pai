from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt

from config import settings
from db.client import DatabaseClient
from services.auth_service import AuthService
from services.basket_service import BasketService
from services.catalog_service import CatalogService
from services.order_service import OrderService

_db: DatabaseClient | None = None
_basket_service: BasketService | None = None
_catalog_service: CatalogService | None = None
_auth_service: AuthService | None = None
_order_service: OrderService | None = None


def init_dependencies(database_path: str) -> None:
    global _db, _basket_service, _catalog_service, _auth_service, _order_service
    _db = DatabaseClient(database_path)
    _basket_service = BasketService(_db)
    _catalog_service = CatalogService(_db)
    _auth_service = AuthService(_db)
    _order_service = OrderService(_db, _basket_service)


def get_db() -> DatabaseClient:
    assert _db is not None
    return _db


def get_catalog_service() -> CatalogService:
    assert _catalog_service is not None
    return _catalog_service


def get_basket_service() -> BasketService:
    assert _basket_service is not None
    return _basket_service


def get_auth_service() -> AuthService:
    assert _auth_service is not None
    return _auth_service


def get_order_service() -> OrderService:
    assert _order_service is not None
    return _order_service


def _invalid_session() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Your session has expired or is invalid. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        raise _invalid_session()
    email = payload.get("sub")
    if not isinstance(email, str):
        raise _invalid_session()
    return email


def get_current_user_email(
    authorization: str | None = Header(default=None),
) -> str | None:
    """The signed-in user's email, or None when no credential was sent.

    A credential that was sent but is expired, tampered with or malformed is
    rejected outright; there is no anonymous fallback anywhere in the shop.
    """
    if authorization is None:
        return None
    if not authorization.startswith("Bearer "):
        raise _invalid_session()
    token = authorization.removeprefix("Bearer ").strip()
    return _decode_token(token)


def require_authenticated_user(
    user_email: str | None = Depends(get_current_user_email),
) -> str:
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return user_email


def require_role(*roles: str):
    """A dependency that admits only signed-in users with one of ``roles``.

    Every organiser-only and supplier-only route is guarded by this, so a
    wrong role is always a 403 and never a silent no-op.
    """

    def check(email: str = Depends(require_authenticated_user)) -> str:
        user = get_auth_service().current_user(email)
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action needs the {' or '.join(roles)} role",
            )
        return email

    return check


require_organiser = require_role("organiser")
require_supplier = require_role("supplier")
