from flask import Flask, request
import lmdb
import os
import json
import hashlib
import base64

master = Flask(__name__)

class FileCache:
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

fc = FileCache(os.environ['DB'])

def shard_put(uri):
    pass

def key_to_path(key):
    md5 = hashlib.md5(key).digest()
    print(md5)
    b64key = base64.b64encode(key).decode('utf-8')

    return "/%02x/%02x/%s" % (md5[0], md5[1], b64key)

def key_to_shard(key):
    """Pick the shard for this key by hashing it with the 
    volume server name. Choose the volume that produces the 
    largest number. TODO: rebalance shards if more are added
    (during runtime or not)"""
    highest_num = 0
    shard_url = None

    for s in os.environ['SHARDS'].split(','):
        shard = s.encode('utf-8')
        string = shard + key
        md5_int = int.from_bytes(hashlib.md5(string).digest(), byteorder='big', signed=False)
        if md5_int > highest_num:
            highest_num = md5_int
            shard_url = shard
    return shard_url
    

@master.route('/<key>', methods=['GET', 'PUT'])
def req_handler(key):
    if request.method == 'PUT':
        key = key.encode('utf-8')
        if not request.content_length:
            return 'Empty content', 411
        # Return error if trying to put an already existing key
        value = next(request.form.keys())
        if fc.get(key) is not None:
            return 'Key %s already exists' % key, 409
        
        shard = key_to_shard(key)

        shard_server = 'http://%s%s' % (shard, key_to_path(key))
        return key_to_path(key)
    elif request.method == 'GET':
        value = fc.get(key)
        if value is None:
            return ('Key with value: %s not found.' % key, 404)
        # 
    else:
        return 'Unrecognized command'