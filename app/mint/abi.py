MINT_CONTRACT_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_tokenURI", "type": "bytes32"},
            {"internalType": "bytes32", "name": "_tokenAttribute", "type": "bytes32"},
        ],
        "name": "getTokenURIAndAttributeHash",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "pure",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "_tokenAttribute", "type": "bytes32"}
        ],
        "name": "tokenAttributeExists",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]
