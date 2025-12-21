import hashlib
import json
from time import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: int
    timestamp: float = field(default_factory=time)
    signature: str = "" # Placeholder for simulation
    memo: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def calculate_hash(self) -> str:
        tx_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(tx_string.encode()).hexdigest()

@dataclass
class Block:
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    hash: str = ""

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_tx = Transaction("0", "0", 0, memo="Genesis Block")
        self.create_block(previous_hash="0", transactions=[genesis_tx])

    def create_block(self, previous_hash: str = None, transactions: List[Transaction] = None) -> Block:
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time(),
            transactions=transactions if transactions is not None else self.pending_transactions,
            previous_hash=previous_hash or self.get_latest_block().hash
        )
        block.hash = block.calculate_hash()

        # Reset pending transactions if we consumed them
        if transactions is None:
            self.pending_transactions = []

        self.chain.append(block)
        return block

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: int, memo: str = "") -> int:
        transaction = Transaction(sender, recipient, amount, memo=memo)
        self.pending_transactions.append(transaction)
        return self.get_latest_block().index + 1

    def mine_pending_transactions(self, miner_address: str):
        # In a real chain, we'd do proof of work here.
        # For this game simulation, we just package them into a block.
        # Reward transaction
        # self.pending_transactions.append(Transaction("System", miner_address, 1, memo="Mining Reward"))

        block = self.create_block()
        return block

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def get_balance_of_address(self, address: str) -> int:
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount
        return balance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "length": len(self.chain),
            "latest_block": {
                "index": self.get_latest_block().index,
                "hash": self.get_latest_block().hash,
                "timestamp": self.get_latest_block().timestamp
            }
        }

# Global Blockchain Instance
game_blockchain = Blockchain()
