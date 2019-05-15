#!/usr/bin/env python

import redis
import argparse

r = None
r2 = None
dryrun = False

print('### Dryrun = {} ###'.format(dryrun))

def handle_special(k):
    ktype = r.type(k)
    print('handling key {} of type {}'.format(k, ktype))
    if not dryrun:
        r2.delete(k)  # remove any existing key before we add to it
    if ktype == 'list':
        v = r.lrange(k, 0, -1)
        if not dryrun:
            r2.rpush(k, *v)
    elif ktype == 'hash':
        v = r.hgetall(k)
        if not dryrun:
            r2.hmset(k, v)
    elif ktype == 'set':
        v = r.smembers(k)
        if not dryrun:
            r2.sadd(k, *v)
    else:
        print('yow... type {} not handled!!!'.format(ktype))
    
if __name__ == '__main__':
    # source redis client
    # r = redis.Redis(host='localhost', port=7000, db=0, password='db29db89c56a993547c34b0530911705a13318302c06585af5d57fce2bea7e24')
    r = redis.Redis(host='localhost', port=6379, db=0)
    # target redis client
    #r2 = redis.Redis(host='localhost', port=7000, db=3, password='db29db89c56a993547c34b0530911705a13318302c06585af5d57fce2bea7e24')
    r2 = redis.Redis(host='localhost', port=6379, db=3)

    klist = r.keys('*')
    print('Number of keys: {}'.format(len(klist)))
    vlist = r.mget(klist)
    cnt = 0
    removed = 0
    # do this in reverse order to maintain indexing
    for i in reversed(range(len(vlist))):
        if 'OFFSET' in klist[i]:
            print('removing {}'.format(klist[i]))
            del klist[i]
            del vlist[i]
            removed += 1
        if vlist[i] is None:
            handle_special(klist[i])
            del klist[i]
            del vlist[i]
            cnt += 1
    print('# of non-string types: {}'.format(cnt))
    print('# of removed keyss: {}'.format(removed))
    if not dryrun:
        remaining = len(klist)
        batchsize = 10000
        start = 0
        while remaining > 0:
            print('remaining: {}'.format(remaining))
            batch = min(batchsize, remaining)
            mapping = dict(zip(klist[start:start+batch], vlist[start:start+batch]))
            r2.mset(mapping)
            remaining -= batch
            start += batch

