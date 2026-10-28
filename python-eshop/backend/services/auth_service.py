from datetime import datetime, timedelta, timezone

from jose import jwt

from config import settings
from db.client import DatabaseClient
from models.entities import User
from services.passwords import hash_password, verify_password


class DuplicateEmailError(Exception):
    pass


class AuthService:
    def __init__(self, db: DatabaseClient):
        self.db = db

    def login(self, email: str, password: str) -> tuple[str, str, str]:
        user = self.db.get_user_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        token = self._create_token(user.email)
        return token, user.email, user.role

    def create_account(self, email: str, password: str, role: str) -> User:
        if self.db.get_user_by_email(email):
            raise DuplicateEmailError("An account with that email already exists")
        return self.db.create_user(email, hash_password(password), role)

    def change_password(self, email: str, current_password: str, new_password: str) -> None:
        user = self.current_user(email)
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        self.db.update_password(user.email, hash_password(new_password))

    def find_user(self, email: str) -> User | None:
        return self.db.get_user_by_email(email)

    def current_user(self, email: str) -> User:
        user = self.find_user(email)
        if not user:
            raise ValueError("Unknown user")
        return user

    def _create_token(self, email: str) -> str:
        expire = timedelta(minutes=settings.jwt_expire_minutes)
        payload = {"sub": email, "exp": datetime.now(timezone.utc) + expire}
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
