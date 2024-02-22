# Module 2: Create a cryptocurrency

# Importing the packages

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
import threading

# Part 1: Building a blockchain


class Blockchain:

    def __init__(self):
        self.__chain = []
        self.__transactions = []
        self.create_block(proof=1, previous_hash="0")
        self.__nodes = set()

    def create_block(self, proof, previous_hash):
        block = {
            "index": self.get_length(self.__chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash,
            "transactions": self.__transactions
        }
        self.__transactions = []
        self.__chain.append(block)
        return block

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False

        while not check_proof:
            hash_operation = self.proof_problem(new_proof, previous_proof)
            if self.is_hash_valid(hash_operation):
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    def is_chain_valid(self, chain):
        previous_block = chain[0]

        for current_block in chain[1:]:
            is_two_hash_same = current_block["previous_hash"] == self.hash(
                previous_block)
            is_proof_problem_pass = self.is_hash_valid(
                self.proof_problem(current_block["proof"],
                                   previous_block["proof"]))
            if not is_two_hash_same or not is_proof_problem_pass:
                return False
            previous_block = current_block

        return True

    def get_chain(self):
        return self.__chain

    def get_previous_block(self):
        return self.__chain[-1]

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_problem(self, new_proof, previous_proof):
        return hashlib.sha256(str(new_proof**2 -
                                  previous_proof**2).encode()).hexdigest()

    def is_hash_valid(self, hash):
        return hash[:4] == "0000"

    def get_length(self, chain):
        return len(chain)

    def add_transaction(self, sender, receiver, amount):
        self.__transactions.append({
            "sender": sender,
            "receiver": receiver,
            "amount": amount
        })
        return self.get_previous_block()["index"] + 1

    def add_node(self, address):
        parsed_url = urlparse(address)
        self.__nodes.add(parsed_url.netloc)

    def replace_chain(self):
        network = self.__nodes
        longest_chain = None
        max_length = self.get_length(self.__chain)
        for node in network:
            response = requests.get(f"nttp://{node}/get_chain")
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                if length > max_length and self.is_chain_valid(length):
                    max_length = chain
                    longest_chain = chain

        if longest_chain:
            self.__chain = longest_chain
            return True

        return False

    def get_nodes(self):
        return self.__nodes


# Part 2: Mining out blockchain

# Creating an address for the node on port 5000
node_address = str(uuid4()).replace("-", "")

# Creating a web app
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a blockchain
blockchain = Blockchain()


# Mining a new block
@app.route("/mine_block", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block["proof"]
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(node_address, app.root_path, 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {"message": "mining block success!", **block}

    return jsonify(response), 200


# Getting the full blockchain
@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = {
        "message": "getting chain success!",
        "chain": blockchain.get_chain(),
        "length": blockchain.get_length(blockchain.get_chain())
    }

    return jsonify(response), 200


# Checking the blockchain is valid
@app.route("/is_valid", methods=["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.get_chain())
    response = {
        "message": "Checking chain success!",
        "length": blockchain.get_length(blockchain.get_chain()),
        "is_chain_valid": is_valid
    }

    return jsonify(response), 200


# Adding a new transaction to the blockchain
@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    json = request.get_json()
    transaction_keys = ["sender", "receiver", "amount"]
    if not all(key in json for key in transaction_keys):
        return "key(s) in of the transactions is missing", 400
    index = blockchain.add_transaction(json["sender"], json["receiver"],
                                       json["amount"])
    response = {"message": f"This transaction will be added to block {index}"}

    return jsonify(response), 201


# Part 3: Decentralizing the blockchain


# Connecting new nodes
@app.route("/connect_node", methods=["POST"])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)

    response = {
        "message":
        "All the nodes are now connected. The Hadcoin Blockchain now contains the following nodes:",
        "total_nodes": list(blockchain.get_nodes())
    }

    return jsonify(response), 201


# Replacing the chain by the longest chain if needed
@app.route("/replace_chain", methods=["GET"])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    response = {
        "message": "Replacing chain progress completed!",
        "chain": blockchain.get_chain(),
        "is_chain_valid": is_chain_replaced
    }

    return jsonify(response), 200


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
