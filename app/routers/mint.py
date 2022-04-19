import json
from fastapi import APIRouter, Request, Body, HTTPException
from typing import Dict
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


@router.get("/")
async def mint_get(req: Request):
    request_args: Dict[str, str] = dict(req.query_params)
    print(request_args)

    input_traits_str: str = request_args["traits"]
    print(input_traits_str)

    input_traits: InputTraits = json.loads(input_traits_str)
    print(input_traits)

    mint_data = mint(input_traits)

    return {"success": True, "data": mint_data}


@router.post("/")
async def mint_post(payload: Dict[str, InputTraits] = Body(...)):
    print(payload)

    input_traits: InputTraits = payload["traits"]
    print(input_traits)

    mint_data = mint(input_traits)

    return {"success": True, "data": mint_data}
