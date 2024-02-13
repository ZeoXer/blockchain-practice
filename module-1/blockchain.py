# Module 1: Create a blockchain

# Importing the packages

import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1: Building a blockchain


class Blockchain:

    def __init__(self):
        self.__chain = []
        self.create_block(proof=1, previous_hash="0")

    def create_block(self, proof, previous_hash):
        block = {
            "index": self.get_length(self.__chain) + 1,
            "timestamp": str(datetime.datetime.now()),
            "proof": proof,
            "previous_hash": previous_hash
        }
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


# Part 2: Mining out blockchain

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


# Running the app
app.run(host="0.0.0.0", port=5000)
