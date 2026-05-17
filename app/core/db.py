from collections.abc import Awaitable, Callable
from functools import wraps
from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.logging import setup_logger

log = setup_logger(__name__)


def managed_db_session[**P, R](func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Look for session in kwargs by parameter name 'db_session'
        db_session = cast(AsyncSession, kwargs.get('db_session'))

        if db_session is None:
            log.warning('No db_session found in kwargs, skipping session management')
            return await func(*args, **kwargs)
        else:
            try:
                result = await func(*args, **kwargs)
                log.debug('Got successful result. Commit DB changes.: %s', result)
                await db_session.commit()
            except Exception as exc:
                log.warning('Exception caught. Roll DB changes back.: %s', exc)
                if db_session is not None:
                    await db_session.rollback()
                raise
            else:
                return result

    return wrapper


class DBSessionMiddleware:
    def __init__(self, app: ASGIApp, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope['type'] == 'http':
            scope['db_session'] = self.session_factory()
            try:
                await self.app(scope, receive, send)
            finally:
                db_session = scope.pop('db_session', None)
                if db_session is not None:
                    await db_session.close()
        else:
            await self.app(scope, receive, send)
