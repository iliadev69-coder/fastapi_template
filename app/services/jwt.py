from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from app.schemas.auth import AuthToken, TokenParamsSchema
from app.schemas.base import BaseTokenParamsSchema


class JWTService:
    def __init__(
        self,
        jwt_issuer: str,
        jwt_secret_key: str,
        jwt_algorithms: list[str],
        access_token_exp_delta: timedelta,
        jwt_not_before_gap: timedelta,
    ) -> None:
        self.jwt_issuer = jwt_issuer
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithms = jwt_algorithms
        self.access_token_exp_delta = access_token_exp_delta
        self.jwt_not_before_gap = jwt_not_before_gap

    async def generate_access_token(
        self,
        user_id: UUID,
        when: datetime,
    ) -> AuthToken:
        token = self.encode_token(
            token_params=TokenParamsSchema(),
            sub=user_id,
            exp_delta=self.access_token_exp_delta,
            when=when,
        )
        return AuthToken(token=token, expires_at=when + self.access_token_exp_delta)

    def decode_token(self, token: str) -> dict[str, Any]:
        decoded: dict[str, Any] = jwt.decode(
            jwt=token,
            key=self.jwt_secret_key,
            algorithms=self.jwt_algorithms,
        )
        return decoded

    def encode_token(
        self,
        token_params: BaseTokenParamsSchema,
        sub: UUID,
        exp_delta: timedelta,
        when: datetime,
    ) -> str:
        payload = {
            **token_params.model_dump(mode='json'),
            'sub': str(sub),
            'iss': self.jwt_issuer,
            'exp': (when + exp_delta).timestamp(),
            'nbf': (when - self.jwt_not_before_gap).timestamp(),
            'iat': when.timestamp(),
        }
        return jwt.encode(
            payload=payload,
            key=self.jwt_secret_key,
            algorithm=self.jwt_algorithms[0],
        )
