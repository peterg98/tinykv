# Manual rebalance strategy: Create new shard servers manually via /scripts/shard.sh
# and master runs this script when it receives a rebalance request

# NOTE: Might have some complex issues due to rebalancing while accepting requests

import sys
import lmdb
import hashlib
import requests 

def shard_put(filepath, data):
    try:
        req = requests.put(filepath, data)
        # 201 is a new file, 204 is an overwrite
        response_code = req.status_code in [201, 204]
    except Exception as e:
        print(e)
        return False
    return response_code

def shard_delete(filepath):
    try:
        req = requests.delete(filepath)
        ret = req.status_code == 204
    except Exception:
        return False
    return ret

def key_to_shard(key, shards):
    pass

def key_to_path(key):
    md5 = hashlib.md5(key.encode('utf-8')).digest()
    # encode the value into a base64 string as the file name. Inside
    # the file is the unencoded value
    b64key = base64.b64encode(key.encode('utf-8')).decode('utf-8')

    return "/%02x/%02x/%s" % (md5[0], md5[1], b64key)

# Example call: python3 rebalance.py localhost:3001,localhost:3002 /tmp/cachedb

if __name__ == '__main__':
    shards = sys.argv[1].split(',')
    cachedir = sys.argv[2]

    fc = lmdb.open(cachedir)
    if not fc:
        sys.exit('Unable to locate lmdb dump in %s. Aborting.' % cachedir)
    
    # since we use consistent hashing for sharding, this rebalance operation
    # is quite costly. Re-hashing each existing key is likely going to put it
    # in a different location

    with fc.begin(write=True) as txn:
        cursor = txn.cursor()
        # Iterate over all current key/values and rehash
        moved, total = 0, 0
        for key, value in cursor:
            remote = key_to_shard(key, shards)
            path = key_to_path(key)
            # unlink file in old shard and place in in new location if 
            # hash is different. do nothing otherwise
            new_shard_loc = 'http://%s%s' % (remote, path)
            if new_shard_loc != value:
                # get file content
                print('Moving key %s at location %s...' % (key, value))

                txn.delete(key.encode('utf-8'))
                content = requests.get(value)
                txn.put(key.encode('utf-8'), json.dumps(content).encode('utf-8'))
                shard_delete(value)
                shard_put(new_shard_loc, content)
                
                print('New key %s at location %s' % (key, new_shard_loc))
                moved += 1
            else:
                print('Key %s is unchanged' % (key))
            total += 1
        print('%d out of %d were redistributed.' % (moved, total))