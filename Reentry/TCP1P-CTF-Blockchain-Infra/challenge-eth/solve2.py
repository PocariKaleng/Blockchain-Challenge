from foundpy import config

from solve import solve_instance


RPC_URL = "http://localhost:48334/<INSTANCE_UUID>"
PRIVKEY = "<PLAYER_PRIVATE_KEY>"
SETUP_CONTRACT_ADDR = "<SETUP_CONTRACT_ADDR>"


if __name__ == "__main__":
    config.setup(
        rpc_url=RPC_URL,
        privkey=PRIVKEY,
    )
    solve_instance(SETUP_CONTRACT_ADDR)
