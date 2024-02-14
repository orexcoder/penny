import time
import random

from termcolor import cprint
from eth_account import Account
from web3 import Web3

from config import contract_abi, TRANSACTION_DELAY_FROM, TRANSACTION_DELAY_TO

rpc_url = "https://1rpc.io/base"
web3 = Web3(Web3.HTTPProvider(rpc_url))

print("Connected:", web3.is_connected())

file_path = 'keys.txt'
private_keys = []

# Open the file and read the lines
try:
    with open(file_path, 'r') as file:
        for line in file:
            private_key = line.strip()
            if private_key:
                private_keys.append(private_key)
except FileNotFoundError:
    print(f"The file {file_path} was not found.")

contract_address = Web3.to_checksum_address("0xB3Da098a7251A647892203e0C256b4398d131a54")

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

success_file_path = 'success.txt'

def append_success_key(key):
    try:
        with open(success_file_path, 'a') as file:
            file.write(key + '\n')
    except Exception as e:
        print(f"Error writing key to file: {e}")


for key in private_keys:

    time_sleep_txn = random.randint(TRANSACTION_DELAY_FROM, TRANSACTION_DELAY_TO)
    time.sleep(time_sleep_txn)
    account = web3.eth.account.from_key(key)
    account_addr = web3.to_checksum_address(account.address)
    nonce = web3.eth.get_transaction_count(account_addr)

    transaction = contract.functions.mint().build_transaction({
        'chainId': 8453, #base
        'gasPrice':  round(1.15*web3.eth.gas_price),
        'nonce': nonce,
        'gas': 40000
    })

    # estimated_gas = web3.eth.estimate_gas(transaction)

    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=key)

    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        print("Transaction receipt:", tx_receipt)
        cprint(f'\n>>> Transaction success | https://basescan.org/tx/{tx_hash.hex()} ', 'green')
        append_success_key(key)

    except Exception as e:
        cprint(f'\n>>> Transaction failed {private_key} | \n{str(e)}', 'red')

