#!/usr/bin/env python

import argparse
import json
import re
import subprocess
import base64
import os
import tempfile

conf = '''
[redis-cli]
client=yes
accept=127.0.0.1:REDIS_LOCAL_PORT
connect=REDIS_HOST:REDIS_PORT
verify=2
checkHost=REDIS_HOST
CAfile=REDIS_CERT_FILE
'''

def parse_args():
    parser = argparse.ArgumentParser(description='Create stunnel config for IBM Redis')
    parser.add_argument('-p', '--port', type=int, default=6379, help='Local port for client (e.g. redis-cli)')
    parser.add_argument('-c', '--credentials-file', required=True, help='JSON credentials file')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    with open(args.credentials_file) as f:
        creds = json.load(f)
    (cfd, cert_path) = tempfile.mkstemp()

    comp_url = creds['connection']['rediss']['composed'][0]
    m = re.match(r'^rediss://[^:]+:([^@]+)@([^:]+):(\d+)', comp_url)
    
    conf = conf.replace('REDIS_LOCAL_PORT', str(args.port))
    conf = conf.replace('REDIS_HOST', m.group(2))
    conf = conf.replace('REDIS_PORT', m.group(3))
    conf = conf.replace('REDIS_CERT_FILE', cert_path)

    with open(cert_path, 'w') as f:
        cert_base64 = creds['connection']['rediss']['certificate']['certificate_base64']
        f.write(base64.b64decode(cert_base64))
    os.close(cfd)
    
    print('AUTH {}'.format(m.group(1)))

    print('Creating stunnel on local port {} to redis'.format(args.port))
    subprocess.call('echo "{}" | stunnel -fd 0'.format(conf), shell=True)
    os.remove(cert_path)
