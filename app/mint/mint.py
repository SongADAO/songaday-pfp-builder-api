"""
Handle generating, pinning and signing an image and metadata for a NFT mint
"""

from .attributes import (
    input_traits_to_traits,
    trait_hex_to_decimal,
    traits_to_attributes,
    traits_to_hex,
)
from .publish import publish
from .sign import sign
from .typings import (
    Attributes,
    InputTraits,
    MintResponse,
    PublishResponse,
    Traits,
)


def mint(approved_address: str, input_traits: InputTraits) -> MintResponse:
    """
    Take a set of traits, generate the image and metadata, and sign it
    """

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

    signature: str = sign(
        approved_address,
        published["metadata_ipfs_hash_base16_bytes32"],
        traits_hex,
    )

    return {
        "approved_address": approved_address,
        "traits": traits,
        "traits_hex": traits_hex,
        "traits_decimal": traits_decimal,
        "attributes": attributes,
        "published": published,
        "signature": signature,
    }
