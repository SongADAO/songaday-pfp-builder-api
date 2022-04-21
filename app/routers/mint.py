"""
Routes for Mint API
"""

import ast
import json
from typing import Dict, Union
from fastapi import APIRouter, Request, Body, HTTPException
from .config import URL_PREFIX
from ..mint.mint import mint
from ..mint.typings import InputTraits

router = APIRouter(
    prefix=f"{URL_PREFIX}/mint",
    tags=["mint"],
    responses={404: {"description": "Not found"}},
)


# http://localhost:5000/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}
# https://idchain.songadao.org/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}


def format_error(error: Union[str, Dict[str, str], Exception]):
    """
    Format errors into returnable json
    """

    code = 0
    message = str(error)

    print(str(error))

    try:
        error = ast.literal_eval(str(error))
    except Exception:
        pass

    if isinstance(error, dict) and ("code" in error):
        code = error["code"]

    if isinstance(error, dict) and ("message" in error):
        message = error["message"]

    print(code)
    print(message)

    return {"code": code, "message": message}


def error400(error: Union[str, Dict[str, str], Exception]):
    """
    Handle returning a HTTP 400 error
    """

    raise HTTPException(status_code=400, detail=format_error(error))


@router.get("/")
async def mint_get(req: Request):
    """
    Mint API Route (GET)
    """

    payload: Dict[str, str] = dict(req.query_params)

    if "traits" not in payload:
        error400("Missing traits parameter")

    try:
        input_traits: InputTraits = json.loads(payload["traits"])
        print(input_traits)
    except Exception:
        error400("Malformed traits parameter")

    try:
        mint_data = mint(input_traits)

        return {"data": mint_data}
    except Exception as error:
        error400(error)


@router.post("/")
async def mint_post(payload: Dict[str, InputTraits] = Body(...)):
    """
    Mint API Route (POST)
    """

    print(payload)

    if "traits" not in payload:
        error400("Missing traits parameter")

    input_traits: InputTraits = payload["traits"]
    print(input_traits)

    try:
        mint_data = mint(input_traits)

        return {"data": mint_data}
    except Exception as error:
        error400(error)
