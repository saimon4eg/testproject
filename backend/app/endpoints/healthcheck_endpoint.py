from fastapi import APIRouter, Response

router = APIRouter()


@router.get('/healthcheck', include_in_schema=False)
async def healthcheck():
    """
        permission: None
    """
    return Response(status_code=200)
