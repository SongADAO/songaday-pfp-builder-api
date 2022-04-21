"""
Minting typings
"""

import io
from typing import Dict, Literal, TypedDict


InputTraits = Dict[str, str]


class LayerOption(TypedDict):
    id: int
    name: str
    ext: str
    thumbExt: str
    cost: int


LayerOptions = list[LayerOption]


class Layer(TypedDict):
    id: int
    name: str
    display: str
    default: str
    options: LayerOptions


Layers = list[Layer]


class Attribute(TypedDict):
    trait_type: str
    value: str


Attributes = list[Attribute]


class Trait(TypedDict):
    id: int
    name: str
    display: str
    option: LayerOption


Traits = list[Trait]


class MetaData(TypedDict):
    name: str
    description: str
    attributes: Attributes
    image: str


class ResourcePaths(TypedDict):
    input: str
    output: str


class PinataHeaders(TypedDict):
    pinata_api_key: str
    pinata_secret_api_key: str


PinataResponse = Dict[str, str]


PinataFiles = list[tuple[Literal["file"], tuple[str, io.BufferedReader]]]


class PublishResponse(TypedDict):
    image_ipfs_hash: str
    metadata_ipfs_hash: str
    metadata_ipfs_hash_base16: str
    metadata_ipfs_hash_base16_bytes32: str


class PinataKeyValues(TypedDict):
    traitsHex: str


class SignResponse(TypedDict):
    signature: str


class MintResponse(TypedDict):
    traits: Traits
    traits_hex: str
    traits_decimal: int
    attributes: Attributes
    published: PublishResponse
    signature: str
