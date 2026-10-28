from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_auth_service, require_organiser
from models.schemas import CreateUserRequest, CurrentUserResponse
from services.auth_service import AuthService, DuplicateEmailError

router = APIRouter(
    prefix="/api/organiser",
    tags=["organiser"],
    dependencies=[Depends(require_organiser)],
)


@router.post("/users", response_model=CurrentUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: CreateUserRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        user = service.create_account(body.email, body.password, body.role)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return CurrentUserResponse(email=user.email, role=user.role)
