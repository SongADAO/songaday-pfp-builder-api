import base64, pathlib, json, requests, math
from PIL import Image
from .config import MINT_RESOURCE_PATH, PINATA_API_KEY, PINATA_SECRET_API_KEY
from .typings import *


def ipfs_hash_to_base16(ipfs_hash: str) -> str:
    ipfs_hash_upper: str = ipfs_hash.upper()

    if ipfs_hash_upper.startswith("B") == False:
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

    ipfs_hash_base16_bytes: bytes = base64.b16encode(ipfs_hash_upper_no_prefix_bytes)

    ipfs_hash_base16: str = "f" + ipfs_hash_base16_bytes.decode("utf-8").lower()

    return ipfs_hash_base16


def ipfs_hash_base16_to_bytes32(ipfs_hash_base16: str) -> str:
    ipfs_hash_base16_upper: str = ipfs_hash_base16.upper()

    if ipfs_hash_base16_upper.startswith("F01551220") == False:
        raise Exception("Invalid IPFS Hash Prefix")

    ipfs_hash_base16_bytes32: str = "0x" + ipfs_hash_base16_upper[9:].lower()

    return ipfs_hash_base16_bytes32


def get_paths(output_folder_name: str) -> ResourcePaths:
    resource_path: str = MINT_RESOURCE_PATH

    paths: ResourcePaths = {
        "input": "{}/input".format(resource_path),
        "output": "{}/output/{}".format(resource_path, output_folder_name),
    }

    # Create directory if it doesn't exist
    pathlib.Path(paths["output"]).mkdir(parents=True, exist_ok=True)

    return paths


def create_image(
    paths: ResourcePaths,
    file_name: str,
    traits: Traits,
) -> str:
    # Setup paths
    output_path: str = "{}/{}".format(paths["output"], file_name)

    # Get the blank first layer. This is used for sizing.
    placeholder_image_path: str = "{}/placeholder.png".format(paths["input"])
    image = Image.open(placeholder_image_path).convert("RGBA")

    # Start the new composite image with the blank layer
    composite_image = Image.new("RGBA", image.size)
    composite_image.paste(image, (0, 0), image)

    # Add each attribute's layer
    for trait in traits:
        trait_layer_folder_name: str = trait["name"].lower()

        trait_layer_id_number: str = str(trait["option"]["id"]).lower().rjust(3, "0")

        trait_layer_file_name: str = trait["option"]["name"].lower()

        trait_layer_file_ext: str = trait["option"]["ext"].lower()

        image_path: str = "{}/{}/{}-{}.{}".format(
            paths["input"],
            trait_layer_folder_name,
            trait_layer_id_number,
            trait_layer_file_name,
            trait_layer_file_ext,
        )
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
    # Setup paths
    output_path: str = "{}/{}".format(paths["output"], file_name)

    # Make IPFS Hash a URL
    image_ipfs_url: str = "ipfs://{}".format(image_ipfs_hash)

    # Assemble metadata
    metadata: MetaData = {
        "name": "Song-A-Day PFP",
        "description": "Song-A-Day PFP",
        "attributes": attributes,
        "image": image_ipfs_url,
    }

    # Write the metadata to disk
    with open(output_path, "w") as outfile:
        json.dump(metadata, outfile)

    return output_path


def pin_file_to_ipfs(
    path: str,
    name: str,
    keyvalues: PinataKeyValues,
) -> str:
    pinata_api_url: str = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    files: PinataFiles = [
        ("file", (name, open(path, "rb"))),
    ]

    headers: PinataHeaders = {
        "pinata_api_key": PINATA_API_KEY,
        "pinata_secret_api_key": PINATA_SECRET_API_KEY,
    }

    data = {
        "pinataMetadata": json.dumps(
            {
                "keyvalues": keyvalues,
            }
        ),
        "pinataOptions": json.dumps({"cidVersion": 1}),
    }
    # print(data)

    response: requests.Response = requests.post(
        url=pinata_api_url, headers=headers, files=files, data=data
    )

    if response.ok == False:
        print("Failed to PIN to IPFS: {}".format(name))
        raise Exception("Failed to PIN to IPFS")

    responseJson: PinataResponse = response.json()
    print(response.json())

    if type(responseJson) is not dict or "IpfsHash" not in responseJson:
        print("Failed to get IPFS hash: {}".format(name))
        raise Exception("Failed to get IPFS hash")

    return responseJson["IpfsHash"]


def publish(
    traits: Traits,
    attributes: Attributes,
    traits_hex: str,
) -> PublishResponse:
    metadata_file_name: str = "metadata.json"
    image_file_name: str = "image.png"
    metadata_name: str = "{}-{}".format(traits_hex, metadata_file_name)
    image_name: str = "{}-{}".format(traits_hex, image_file_name)
    keyvalues: PinataKeyValues = {
        "traitsHex": traits_hex,
    }

    paths: ResourcePaths = get_paths(traits_hex)

    image_path: str = create_image(paths, image_file_name, traits)

    image_ipfs_hash: str = pin_file_to_ipfs(image_path, image_name, keyvalues)

    metadata_path: str = create_metadata(
        paths, metadata_file_name, attributes, image_ipfs_hash
    )

    metadata_ipfs_hash: str = pin_file_to_ipfs(metadata_path, metadata_name, keyvalues)

    metadata_ipfs_hash_base16: str = ipfs_hash_to_base16(metadata_ipfs_hash)

    metadata_ipfs_hash_base16_bytes32: str = ipfs_hash_base16_to_bytes32(
        metadata_ipfs_hash_base16
    )

    return {
        "image_ipfs_hash": image_ipfs_hash,
        "metadata_ipfs_hash": metadata_ipfs_hash,
        "metadata_ipfs_hash_base16": metadata_ipfs_hash_base16,
        "metadata_ipfs_hash_base16_bytes32": metadata_ipfs_hash_base16_bytes32,
    }
