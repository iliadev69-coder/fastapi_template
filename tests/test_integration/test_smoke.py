from http import HTTPStatus

from httpx import AsyncClient


async def test_openapi_available(client: AsyncClient) -> None:
    response = await client.get('/openapi.json')
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body['info']['title'] == 'FastAPI Template'


async def test_sign_in_with_missing_user_returns_400(client: AsyncClient) -> None:
    response = await client.post(
        '/auth/sign-in/',
        json={'email': 'noone@example.com', 'password': 'whatever123'},
        headers={'user-agent': 'pytest'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
