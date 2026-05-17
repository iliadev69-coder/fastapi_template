from fastapi import APIRouter

router = APIRouter(tags=['System'])


@router.get('/ping', name='system:ping')
async def ping() -> dict[str, str]:
    return {'status': 'ok'}
