from collections.abc import AsyncIterator

from redis.asyncio import Redis


async def redis_client(url: str) -> AsyncIterator[Redis]:  # type: ignore[type-arg]
    try:
        client = Redis.from_url(url)
        yield client
    finally:
        await client.aclose()  # type: ignore[attr-defined] # pyright: ignore[reportAttributeAccessIssue]
