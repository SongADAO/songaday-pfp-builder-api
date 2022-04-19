import json
from .config import MINT_RESOURCE_PATH
from .typings import *


def input_traits_to_traits(input_traits: InputTraits) -> Traits:
    all_layers: Layers = get_all_layers()

    traits: Traits = []

    for trait_type, value in input_traits.items():
        layer: Layer = get_layer_by_name(all_layers, trait_type)

        # if isinstance(layer["options"], list) == False:
        #     raise Exception("invalid layer options: {}".format(trait_type))

        layer_option: LayerOption = get_layer_option_by_name(layer["options"], value)

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
    sort_traits(traits)

    res_traits = traits[::-1]

    hex_str: str = "0x" + "".join(
        [id_to_hex(trait["option"]["id"]) for trait in res_traits]
    ).rjust(64, "0")

    print(hex_str)

    return hex_str


def trait_hex_to_decimal(hex_str: str) -> int:
    return int(hex_str, 16)


def get_all_layers() -> Layers:
    layers_json_path: str = "{}/config/layers.json".format(MINT_RESOURCE_PATH)

    all_layers = json.load(open(layers_json_path, "r"))

    return all_layers


def get_layer_by_name(layers: Layers, layer_name: str) -> Layer:
    filtered_layers: Layers = [
        layer for layer in layers if layer["name"].lower() == layer_name.lower()
    ]

    if len(filtered_layers) == 0:
        raise Exception("trait does not exist: {}".format(layer_name))

    return filtered_layers[0]


def get_layer_option_by_name(
    layer_options: LayerOptions, layer_option_name: str
) -> LayerOption:
    filtered_layer_options: LayerOptions = [
        layer_option
        for layer_option in layer_options
        if layer_option["name"].lower() == layer_option_name.lower()
    ]

    if len(filtered_layer_options) == 0:
        raise Exception("trait option does not exist: {}".format(layer_option_name))

    return filtered_layer_options[0]


def sort_traits(traits: Traits):
    traits.sort(key=lambda trait: trait["id"])


def id_to_hex(id: int) -> str:
    return "{:02x}".format(id)
