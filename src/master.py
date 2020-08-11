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
            value = txn.get(key.encode('utf-8'))
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

def shard_put(shard_url, data):
    pass


def key_to_path(key):
    md5 = hashlib.md5(key.encode('utf-8')).digest()
    # encode the value into a base64 string as the file name. Inside
    # the file is the unencoded value
    b64key = base64.b64encode(key.encode('utf-8')).decode('utf-8')

    return "/%02x/%02x/%s" % (md5[0], md5[1], b64key)

def key_to_shard(key):
    """Pick the shard for this key by hashing it with the 
    volume server name. Choose the volume that produces the 
    largest number. TODO: rebalance shards if more are added
    (during runtime or not)"""
    highest_num = 0
    shard_url = None

    for s in os.environ['SHARDS'].split(','):
        string = s + key
        print(string)
        md5_int = int.from_bytes(hashlib.md5(string.encode('utf-8')).digest(), byteorder='big', signed=False)
        if md5_int > highest_num:
            highest_num = md5_int
            shard_url = s
    return shard_url
    

@master.route('/<key>', methods=['GET', 'PUT'])
def req_handler(key):
    if request.method == 'PUT':
        if not request.content_length:
            return 'Empty content', 411
        # Return error if trying to put an already existing key
        value = next(request.form.keys())
        if fc.get(key) is not None:
            return 'Key %s already exists' % key, 409
        
        shard = key_to_shard(key)

        shard_server = 'http://%s%s' % (shard, key_to_path(key))

        # put into remote shard first
        if not shard_put(shard_server, value):
            return 'Writing to shard failed.', 500

        # do local write to lmdb after remote PUT succeeds
        #
        # Note: It is possible for remote shard PUT to succeed and 
        # local lmdb write to fail. This only causes an orphan file in the shard,
        # which can be pruned periodically by comparing local db to shards
        if not fc.put(key, {'shard': shard, 'size': })
        return key_to_path(key)
    elif request.method == 'GET':
        value = fc.get(key)
        if value is None:
            return ('Key with value: %s not found.' % key, 404)
        # 
    else:
        return 'Unrecognized command'