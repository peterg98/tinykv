# tinykv

tinykv is a tiny, persistent, and distributed key-value store written in Python. It supports basic partitioning via consistent hashing (called charding by some systems like MongoDB and elasticsearch) and rebalancing.

## Installation

Requires docker and docker-compose. Run `docker-compose build && docker-compose up`.

## Description

Each shard is an nginx file server that allows WebDAV methods. The file server is pre-seeded with empty directories that are 2 levels deep, allowing incoming files to be placed based on their hash. (e.g. localhost:3001/a3/2f/A2D6yHz). This is similar to how git stores its commits.

An LMDB cache stores the key-location (in shard) pairs. (e.g. localhost:3001/e6/a3/zX22aBc). A key-value pair's location is determined by a md5 hash of its corresponding shard and key, and the filename and content is derived from base64-encoded key and value respectively.

Since there are multiple master processes, I've implemented a very crude distributed lock based on Python's multiprocessing Manager.
Haven't tested rebalancing yet but it involves getting a snapshot of all the current keys in the cache and rehashing them: this is pretty costly if there's a lot of keys

## Configuration and usage

In `docker-compose.yml`, expose the port range for both the master and shard servers.

```
Put 'world' with key 'hello':

curl -L -X PUT -d world localhost:3000/hello # Value world is stored at http://localhost:3001/d4/a2/aM2Xcl

Get value with key 'hello':

curl -L localhost:3000/hello # world

Delete value with key 'hello':

curl -L -X DELETE localhost/hello # Delete succeeded.
```