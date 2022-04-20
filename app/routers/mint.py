import ast, json
from fastapi import APIRouter, Request, Body, HTTPException
from typing import Dict, Union
from .config import URL_PREFIX
from ..mint.mint import mint
from ..mint.typings import InputTraits

router = APIRouter(
    prefix="{}/mint".format(URL_PREFIX),
    tags=["mint"],
    responses={404: {"description": "Not found"}},
)


# http://localhost:5000/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}
# https://idchain.songadao.org/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}


def format_error(error: Union[str, Dict[str, str], Exception]):
    code = 0
    message = str(error)

    print(str(error))

    try:
        error = ast.literal_eval(str(error))
    except Exception:
        pass

    if (type(error) is dict) and ("code" in error):
        code = error["code"]

    if (type(error) is dict) and ("message" in error):
        message = error["message"]

    print(code)
    print(message)

    return {"code": code, "message": message}


def error400(error: Union[str, Dict[str, str], Exception]):
    raise HTTPException(status_code=400, detail=format_error(error))


@router.get("/")
async def mint_get(req: Request):
    payload: Dict[str, str] = dict(req.query_params)

    if type(payload) is not dict:
        error400("Missing request parameters")

    if "traits" not in payload:
        error400("Missing traits parameter")

    try:
        input_traits: InputTraits = json.loads(payload["traits"])
        print(input_traits)
    except:
        error400("Malformed traits parameter")

    try:
        mint_data = mint(input_traits)

        return {"data": mint_data}
    except Exception as error:
        error400(error)


@router.post("/")
async def mint_post(payload: Dict[str, InputTraits] = Body(...)):
    print(payload)

    if type(payload) is not dict:
        error400("Missing request parameters")

    if "traits" not in payload:
        error400("Missing traits parameter")

    input_traits: InputTraits = payload["traits"]
    print(input_traits)

    try:
        mint_data = mint(input_traits)

        return {"data": mint_data}
    except Exception as error:
        error400(error)
