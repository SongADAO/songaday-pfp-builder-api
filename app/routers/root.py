from fastapi import APIRouter
from .config import URL_PREFIX

router = APIRouter(
    prefix="{}".format(URL_PREFIX),
    tags=["root"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def root():
    return {"message": "running"}
