from .attributes import (
    input_traits_to_traits,
    traits_to_attributes,
    traits_to_hex,
    trait_hex_to_decimal,
)
from .publish import publish
from .sign import sign
from .typings import Traits, Attributes, PublishResponse, MintResponse, InputTraits


def mint(input_traits: InputTraits) -> MintResponse:
    traits: Traits = input_traits_to_traits(input_traits)
    print(traits)

    traits_hex: str = traits_to_hex(traits)
    print(traits_hex)

    traits_decimal: int = trait_hex_to_decimal(traits_hex)
    print(traits_decimal)

    attributes: Attributes = traits_to_attributes(traits)
    print(attributes)

    published: PublishResponse = publish(traits, attributes, traits_hex)
    print(published)

    signature: str = sign(published["metadata_ipfs_hash_base16_bytes32"], traits_hex)

    return {
        "traits": traits,
        "traits_hex": traits_hex,
        "traits_decimal": traits_decimal,
        "attributes": attributes,
        "published": published,
        "signature": signature,
    }


# def mint(input_traits: InputTraits):
#     signature: str = sign(
#         "0x0000000000000000000000000000000000000000000000000001010101010101",
#         "0x6f0b9c69c458c67dac691aa995ac247b4200d2ffe8dd86088ab7b6099a640f65",
#     )
#     print(signature)

#     return {"signature": signature}
