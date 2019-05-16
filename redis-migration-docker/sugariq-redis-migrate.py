#!/usr/bin/env python

import redis
import argparse
import sys

source = None
target = None

args = None

def handle_args():
    parser = argparse.ArgumentParser(description='Redis migration utility')
    parser.add_argument('-s', '--source-port', type=int, default=6379, help='specify the local source port (default:6379)')
    parser.add_argument('--source-db', type=int, default=0, help='redis db [0-15], default 0')
    parser.add_argument('-t', '--target-port', type=int, required=True, help='local port to reach the target')
    parser.add_argument('--target-db', type=int, default=0, help='redis db [0-15], default 0')
    parser.add_argument('--flushdb', action='store_true', help='flush/clear target db at start')
    parser.add_argument('--danger', action='store_true', help='for safety, this option must be specified if targetting db 0')
    parser.add_argument('-p', '--password', default=None, help='password for the cloud db')
    parser.add_argument('-d', '--dryrun', action='store_true', help='just check db connectivity (no writes)')
    global args
    args = parser.parse_args()

    if args.target_db == 0 and not args.danger:
        print('ERROR: --danger flag must be used if targetting db 0')
        sys.exit(-1)

def handle_special(k):
    ktype = source.type(k)
    print('handling key {} of type {}'.format(k, ktype))
    if not args.dryrun:
        target.delete(k)  # remove any existing key before we modify it
    if ktype == 'list':
        v = source.lrange(k, 0, -1)
        if not args.dryrun:
            target.rpush(k, *v)
    elif ktype == 'hash':
        v = source.hgetall(k)
        if not args.dryrun:
            target.hmset(k, v)
    elif ktype == 'set':
        v = source.smembers(k)
        if not args.dryrun:
            target.sadd(k, *v)
    else:
        print('yow... type {} not handled!!!'.format(ktype))
    
if __name__ == '__main__':

    handle_args()

    source = redis.Redis(host='localhost', port=args.source_port, db=args.source_db)
    target = redis.Redis(host='localhost', port=args.target_port, db=args.target_db, password=args.password)

    if args.dryrun:
        print('### DRYRUN mode -- no DB changes ###')
    elif args.flushdb:
        print('flushing db {}'.format(args.target_db))
        target.flushdb()

    klist = source.keys('*')
    print('Number of keys: {}'.format(len(klist)))
    vlist = source.mget(klist)
    cnt = 0
    removed = 0

    # do this in reverse order to maintain index position
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

    if not args.dryrun:
        remaining = len(klist)
        batchsize = 10000
        start = 0
        while remaining > 0:
            print('remaining: {}'.format(remaining))
            batch = min(batchsize, remaining)
            mapping = dict(zip(klist[start:start+batch], vlist[start:start+batch]))
            target.mset(mapping)
            remaining -= batch
            start += batch

