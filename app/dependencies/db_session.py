from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


def get_db_session(request: Request) -> AsyncSession:
    session: AsyncSession = request.scope['db_session']
    return session
