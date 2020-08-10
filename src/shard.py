from flask import Flask

shard = Flask(__name__)

@app.route('/<key>')
def req_handler(key):
    pass

