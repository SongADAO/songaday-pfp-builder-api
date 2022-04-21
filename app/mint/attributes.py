"""
Handle Determining NFT Metadata Traits and Attributes Based on Input Traits
"""

import json
from .config import MINT_RESOURCE_PATH
from .typings import (
    Attributes,
    InputTraits,
    Layer,
    LayerOption,
    LayerOptions,
    Layers,
    Trait,
    Traits,
)


def input_traits_to_traits(input_traits: InputTraits) -> Traits:
    """
    Convert API input traits into real traits based on traits config
    """

    all_layers: Layers = get_all_layers()

    traits: Traits = []

    for trait_type, value in input_traits.items():
        layer: Layer = get_layer_by_name(all_layers, trait_type)

        layer_option: LayerOption = get_layer_option_by_name(
            layer["options"],
            value,
        )

        trait: Trait = {
            "id": layer["id"],
            "name": layer["name"],
            "display": layer["display"],
            "option": layer_option,
        }

        traits.append(trait)

    sort_traits(traits)

    return traits


def traits_to_attributes(traits: Traits) -> Attributes:
    """
    Convert traits into NFT metadata attributes
    """

    sort_traits(traits)

    attributes: Attributes = []

    for trait in traits:
        attributes.append(
            {
                "trait_type": trait["name"].lower(),
                "value": trait["option"]["name"].lower(),
            }
        )

    return attributes


def traits_to_hex(traits: Traits) -> str:
    """
    Convert traits into NFT on-chain hex representation
    """

    sort_traits(traits)

    res_traits = traits[::-1]

    hex_str: str = "0x" + "".join(
        [id_to_hex(trait["option"]["id"]) for trait in res_traits]
    ).rjust(64, "0")

    print(hex_str)

    return hex_str


def trait_hex_to_decimal(hex_str: str) -> int:
    """
    Convert traits hex into decimal number
    """

    return int(hex_str, 16)


def get_all_layers() -> Layers:
    """
    Get all layers data from layers config json
    """

    layers_json_path: str = f"{MINT_RESOURCE_PATH}/config/layers.json"

    all_layers = json.load(open(layers_json_path, "r", encoding="utf-8"))

    return all_layers


def get_layer_by_name(layers: Layers, name: str) -> Layer:
    """
    Get a layer, from a set, by it's name
    """

    filtered_layers: Layers = [
        layer for layer in layers if layer["name"].lower() == name.lower()
    ]

    if len(filtered_layers) == 0:
        raise Exception(f"trait does not exist: {name}")

    return filtered_layers[0]


def get_layer_option_by_name(options: LayerOptions, name: str) -> LayerOption:
    """
    Get a layer option, from a set, by it's name
    """

    filtered_options: LayerOptions = [
        option for option in options if option["name"].lower() == name.lower()
    ]

    if len(filtered_options) == 0:
        raise Exception(f"trait option does not exist: {name}")

    return filtered_options[0]


def sort_traits(traits: Traits):
    """
    Sort traits by id
    """

    traits.sort(key=lambda trait: trait["id"])


def id_to_hex(id_num: int) -> str:
    """
    Convert id number into hex format
    """

    return f"{id_num:02x}"
