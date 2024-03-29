"""
Handle generating an image and metadata and pinning them to IPFS
"""

import base64
import json
import math
import pathlib
import io
from datetime import datetime
import requests
from PIL import Image
from .config import MINT_RESOURCE_PATH, PINATA_JWT, NFT_STORAGE_JWT
from .typings import (
    Attributes,
    MetaData,
    PinataFiles,
    PinataData,
    # PinataHeaders,
    # NFTStorageHeaders,
    PinataKeyValues,
    PinataResponse,
    NFTStorageResponse,
    PublishResponse,
    ResourcePaths,
    Traits,
)


def ipfs_hash_to_base16(ipfs_hash: str) -> str:
    """
    Convert an IPFS hash to Base16
    """

    ipfs_hash_upper: str = ipfs_hash.upper()

    if not ipfs_hash_upper.startswith("B"):
        raise Exception("Invalid IPFS Hash Prefix")

    ipfs_hash_upper_no_prefix: str = ipfs_hash_upper[1:]

    pad_length: int = math.ceil(len(ipfs_hash_upper_no_prefix) / 8) * 8 - len(
        ipfs_hash_upper_no_prefix
    )

    ipfs_hash_upper_no_prefix_padded: str = ipfs_hash_upper_no_prefix + (
        "=" * pad_length
    )

    ipfs_hash_upper_no_prefix_bytes: bytes = base64.b32decode(
        ipfs_hash_upper_no_prefix_padded
    )

    ipfs_hash_base16_bytes: bytes = base64.b16encode(
        ipfs_hash_upper_no_prefix_bytes,
    )

    return "f" + ipfs_hash_base16_bytes.decode("utf-8").lower()


def ipfs_hash_base16_to_bytes32(ipfs_hash_base16: str) -> str:
    """
    Get image and metadata input/output folders
    """

    ipfs_hash_base16_upper: str = ipfs_hash_base16.upper()

    if not ipfs_hash_base16_upper.startswith("F01551220"):
        raise Exception("Invalid IPFS Hash Prefix")

    ipfs_hash_base16_bytes32: str = "0x" + ipfs_hash_base16_upper[9:].lower()

    return ipfs_hash_base16_bytes32


def get_paths(output_folder_name: str) -> ResourcePaths:
    """
    Get image and metadata input/output folders
    """

    resource_path: str = MINT_RESOURCE_PATH

    timestamp = datetime.timestamp(datetime.now())

    paths: ResourcePaths = {
        "input": f"{resource_path}/input",
        "output": f"{resource_path}/output/{output_folder_name}/{timestamp}",
    }

    # Create directory if it doesn't exist
    pathlib.Path(paths["output"]).mkdir(parents=True, exist_ok=True)

    return paths


def create_image(
    paths: ResourcePaths,
    file_name: str,
    traits: Traits,
) -> str:
    """
    Generate NFT image
    """

    # Setup paths
    output_path: str = f"{paths['output']}/{file_name}"

    # Get the blank first layer. This is used for sizing.
    base_image_path: str = f"{paths['input']}/base.png"
    image = Image.open(base_image_path).convert("RGBA")

    # Start the new composite image with the blank layer
    composite_image = Image.new("RGB", image.size)
    composite_image.paste(image, (0, 0), image)

    # Add each attribute's layer
    for trait in traits:
        trait_layer_folder_name: str = trait["name"].lower()

        trait_layer_id_number: str = str(trait["option"]["id"]).lower()

        trait_layer_id_number_padded: str = trait_layer_id_number.rjust(3, "0")

        trait_layer_file_name: str = trait["option"]["name"].lower()

        trait_layer_file_ext: str = trait["option"]["ext"].lower()

        # pylint: disable=consider-using-f-string
        image_path: str = "{}/{}/{}-{}.{}".format(
            paths["input"],
            trait_layer_folder_name,
            trait_layer_id_number_padded,
            trait_layer_file_name,
            trait_layer_file_ext,
        )
        # pylint: enable=consider-using-f-string

        image = Image.open(image_path).convert("RGBA")
        composite_image.paste(image, (0, 0), image)

    # Write the final image to disk
    composite_image.save(output_path, "PNG")

    return output_path


def create_metadata(
    paths: ResourcePaths,
    file_name: str,
    attributes: Attributes,
    image_ipfs_hash: str,
) -> str:
    """
    Generate NFT metadata
    """

    # Setup paths
    output_path: str = f"{paths['output']}/{file_name}"

    # Make IPFS Hash a URL
    image_ipfs_url: str = f"ipfs://{image_ipfs_hash}"

    # Assemble metadata
    metadata: MetaData = {
        "name": "Song-A-Day PFP",
        "description": "Song-A-Day PFP",
        "attributes": attributes,
        "image": image_ipfs_url,
    }

    # Write the metadata to disk
    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(metadata, outfile)

    return output_path


def pin_file_to_ipfs(
    path: str,
    name: str,
    mime: str,
    keyvalues: PinataKeyValues,
) -> str:
    """
    Pin a file to IPFS
    """

    if NFT_STORAGE_JWT != "":
        return pin_file_to_ipfs_via_nft_storage(path, name, mime)
    elif PINATA_JWT != "":
        return pin_file_to_ipfs_via_pinata(path, name, mime, keyvalues)
    else:
        print("Missing Pinning Service Authorization Token")
        raise Exception("Missing Pinning Service Authorization Token")


def pin_file_to_ipfs_via_pinata(
    path: str,
    name: str,
    mime: str,
    keyvalues: PinataKeyValues,
) -> str:
    """
    Pin a file to IPFS via Pinata
    """

    url: str = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {PINATA_JWT}",
    }

    file: io.BufferedReader = open(path, "rb")

    files: PinataFiles = [
        ("file", (name, file, mime)),
    ]

    data: PinataData = {
        "pinataMetadata": json.dumps({"keyvalues": keyvalues}),
        "pinataOptions": json.dumps({"cidVersion": 1}),
    }

    response: requests.Response = requests.post(
        url=url,
        headers=headers,
        files=files,
        data=data,
    )
    print(response)

    response_json: PinataResponse = response.json()
    print(response_json)

    if response.ok is False:
        print(f"Failed to PIN to IPFS: {name}")
        raise Exception("Failed to PIN to IPFS")

    if "IpfsHash" not in response_json or response_json["IpfsHash"] == "":
        print(f"Failed to get IPFS hash: {name}")
        raise Exception("Failed to get IPFS hash")

    return response_json["IpfsHash"]


def pin_file_to_ipfs_via_nft_storage(path: str, name: str, mime: str) -> str:
    """
    Pin a file to IPFS via NFT.Storage
    """

    url: str = "https://api.nft.storage/upload"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {NFT_STORAGE_JWT}",
    }

    file: io.BufferedReader = open(path, "rb")

    # files: PinataFiles = [
    #     ("file", (name, file, mime)),
    # ]

    data: io.BufferedReader = file

    response: requests.Response = requests.post(
        url=url,
        headers=headers,
        # files=files,
        data=data,
    )
    print(response)

    response_json: NFTStorageResponse = response.json()
    print(response_json)

    if response.ok is False:
        print(f"Failed to PIN to IPFS: {name}")
        raise Exception("Failed to PIN to IPFS")

    if "ok" not in response_json or response_json["ok"] is False:
        print(f"Failed to get IPFS hash: {name}")
        raise Exception("Failed to get IPFS hash")

    if (
        "value" not in response_json
        or "cid" not in response_json["value"]
        or response_json["value"]["cid"] == ""
    ):
        print(f"Failed to get IPFS hash: {name}")
        raise Exception("Failed to get IPFS hash")

    return response_json["value"]["cid"]


def publish(
    traits: Traits,
    attributes: Attributes,
    traits_hex: str,
) -> PublishResponse:
    """
    Generate an image and metadata and pin them to IPFS
    """

    metadata_file_name: str = "metadata.json"
    image_file_name: str = "image.png"
    metadata_name: str = f"{traits_hex}-{metadata_file_name}"
    image_name: str = f"{traits_hex}-{image_file_name}"
    keyvalues: PinataKeyValues = {
        "traitsHex": traits_hex,
    }

    # Get image and metadata paths
    paths: ResourcePaths = get_paths(traits_hex)

    # Create image
    image_path: str = create_image(
        paths,
        image_file_name,
        traits,
    )

    # PIN image
    image_ipfs_hash: str = pin_file_to_ipfs(
        image_path,
        image_name,
        "image/png",
        keyvalues,
    )

    # Create metadata
    metadata_path: str = create_metadata(
        paths,
        metadata_file_name,
        attributes,
        image_ipfs_hash,
    )

    # Pin metadata
    metadata_ipfs_hash: str = pin_file_to_ipfs(
        metadata_path,
        metadata_name,
        "text/json",
        keyvalues,
    )

    # Convert metadata hash to Base16
    metadata_ipfs_hash_base16: str = ipfs_hash_to_base16(
        metadata_ipfs_hash,
    )

    # Convert base16 metadata hash to Bytes32
    metadata_ipfs_hash_base16_bytes32: str = ipfs_hash_base16_to_bytes32(
        metadata_ipfs_hash_base16,
    )

    return {
        "image_ipfs_hash": image_ipfs_hash,
        "metadata_ipfs_hash": metadata_ipfs_hash,
        "metadata_ipfs_hash_base16": metadata_ipfs_hash_base16,
        "metadata_ipfs_hash_base16_bytes32": metadata_ipfs_hash_base16_bytes32,
    }
