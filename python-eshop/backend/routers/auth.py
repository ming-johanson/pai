from fastapi import APIRouter, Depends, HTTPException, Response, status

from dependencies import get_auth_service, require_authenticated_user
from models.schemas import (
    AuthResponse,
    ChangePasswordRequest,
    CurrentUserResponse,
    LoginRequest,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        token, email, role = service.login(body.email, body.password)
        return AuthResponse(access_token=token, email=email, role=role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.get("/me", response_model=CurrentUserResponse)
def me(
    email: str = Depends(require_authenticated_user),
    service: AuthService = Depends(get_auth_service),
):
    user = service.current_user(email)
    return CurrentUserResponse(email=user.email, role=user.role)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest,
    email: str = Depends(require_authenticated_user),
    service: AuthService = Depends(get_auth_service),
):
    try:
        service.change_password(email, body.current_password, body.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
