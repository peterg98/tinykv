from flask import Flask, request
app = Flask(__name__)

@app.route('/<key>', methods=['GET', 'POST', 'PUT'])
def req_handler(key):
    pass
