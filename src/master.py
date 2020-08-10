from flask import Flask, request
import lmdb
import os
import json
app = Flask(__name__)

shards = os.env

class Cache:
    def __init__(self, cachedir):
        self.db = lmdb.open(cachedir)

    def get(self, key):
        with self.db.begin() as txn:
            value = txn.get(key)
            if value is None:
                return None
            return json.loads(value.decode('utf-8'))

    def put(self, key, value):
        with self.db.begin(write=True) as txn:
            old_value = txn.get(key)
            if old_value is None:
                txn.put(key, json.dumps(value).encode('utf-8'))
                return True
            else:
                return False

    def delete(self, key):
        with self.db.begin(write=True) as txn:
            value = txn.get(key)
            if value is None:
                txn.delete(key)
                # Return the deleted value
                return json.loads(value.decode('utf-8'))
            return None

def shard_put(uri):
    pass


@app.route('/<key>', methods=['GET', 'PUT'])
def req_handler(key):
    if request.method == 'PUT':
        # TODO 
        pass
    elif request.method == 'GET':
        pass
    else:
        return 'Unrecognized command'