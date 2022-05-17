"""
Routes for Mint API
"""

import ast
import json
from typing import Dict, Union
from fastapi import APIRouter, Request, Body, HTTPException
from .config import URL_PREFIX
from ..mint.mint import mint
from ..mint.typings import InputTraits, MintRequest
from ..verification.verification import is_verified

router = APIRouter(
    prefix=f"{URL_PREFIX}/mint",
    tags=["mint"],
    responses={404: {"description": "Not found"}},
)


# http://localhost:5000/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}
# https://idchain.songadao.org/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}
# http://localhost:5000/songadao-pfp-builder-api/mint/?traits={"base":"acapella","head":"airport","mood":"angry","beard":"beard","glasses":"hiphop","bottom":"acousticguitar","top":"baltimore"}&address=0xD0D801c1053555726bdCF188F4A55e690C440E74


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

    # Params
    # --------------------------------------------------------------------------

    if "address" not in payload:
        error400("Missing address parameter")

    if "traits" not in payload:
        error400("Missing traits parameter")

    # Verification
    # --------------------------------------------------------------------------
    try:
        if is_verified(payload["address"]) is False:
            raise Exception("Address is not allowed to mint")
    except Exception as error:
        error400(error)

    # Input Traits
    # --------------------------------------------------------------------------

    try:
        input_traits: InputTraits = json.loads(payload["traits"])
        print(input_traits)
    except Exception:
        error400("Malformed traits parameter")

    # Mint
    # --------------------------------------------------------------------------

    try:
        mint_data = mint(payload["address"], input_traits)

        return {"data": mint_data}
    except Exception as error:
        error400(error)


@router.post("/")
async def mint_post(payload: MintRequest = Body(...)):
    """
    Mint API Route (POST)
    """

    print(payload)

    # Params
    # --------------------------------------------------------------------------

    if "address" not in payload:
        error400("Missing address parameter")

    if "traits" not in payload:
        error400("Missing traits parameter")

    # Verification
    # --------------------------------------------------------------------------

    try:
        if is_verified(payload["address"]) is False:
            raise Exception("Address is not allowed to mint")
    except Exception as error:
        error400(error)

    # Input Traits
    # --------------------------------------------------------------------------

    input_traits: InputTraits = payload["traits"]
    print(input_traits)

    # Mint
    # --------------------------------------------------------------------------

    try:
        mint_data = mint(payload["address"], input_traits)

        return {"data": mint_data}
    except Exception as error:
        error400(error)
