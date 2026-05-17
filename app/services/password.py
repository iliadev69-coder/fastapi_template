import hashlib
import secrets

from app.models.user import User
from app.resources.exceptions.auth import AuthenticationError
from app.resources.strings import INCORRECT_USERNAME_OR_PASSWORD


class PasswordService:
    @staticmethod
    def generate_password_hash_and_salt(password: str) -> tuple[str, str]:
        salt = secrets.token_hex(32)

        password_with_salt = password + salt
        password_hash = hashlib.sha256(password_with_salt.encode('utf-8')).hexdigest()

        return password_hash, salt

    @staticmethod
    async def verify(user: User, password: str) -> None:
        if not user.password_hash or not user.password_salt:
            raise AuthenticationError(INCORRECT_USERNAME_OR_PASSWORD)

        password_with_salt = password + user.password_salt
        password_hash = hashlib.sha256(password_with_salt.encode('utf-8')).hexdigest()

        if not secrets.compare_digest(password_hash, user.password_hash):
            raise AuthenticationError(INCORRECT_USERNAME_OR_PASSWORD)
