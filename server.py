import os
from flask import Flask, request
from handler import receive

app = Flask(__name__)

@app.route("/", methods=["POST"])
def webhook():
    # GroupMe sends JSON
    return receive({"body": request.data}, None)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
