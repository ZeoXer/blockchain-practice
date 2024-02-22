from flask import Flask
from hadcoin import app as hadcoin

app1 = Flask(__name__)
app2 = Flask(__name__)
app3 = Flask(__name__)

app1.register_blueprint(hadcoin)
app2.register_blueprint(hadcoin)
app3.register_blueprint(hadcoin)

if __name__ == "__main__":
    app1.run(host="0.0.0.0", port=5001)
    app2.run(host="0.0.0.0", port=5002)
    app3.run(host="0.0.0.0", port=5003)
