#!/usr/bin/python3
import re
import json
import sys
import argparse

conv_int = re.compile(r'^(-?\d+)$')
conv_float = re.compile(r'^(-?\d+\.\d*|-?\d*\.\d+)$')
#
# unquote ints, floats, and booleans at any depth
#
def clean_json(d):
    for k in d:
        if k is None:
            continue
        if isinstance(k, dict) or isinstance(k, list):
            clean_json(k)
            continue
        try:
            # TBD:: double check this 
            if isinstance(d[k], dict) or isinstance(d[k], list):
                clean_json(d[k])
        except:
            pass
        if isinstance(k, str):
            if k in ['notes', 'description']:
                continue
            if not isinstance(d[k], str):
                continue
            if re.match(conv_int, d[k]):
                d[k] = int(d[k])
            elif re.match(conv_float, d[k]):
                d[k] = float(d[k])
            elif d[k] == "false":
                d[k] = False
            elif d[k] == "true":
                d[k] = True


conv_value = re.compile(r', value = (\[\{.*\}\])')
conv_unquoted_strings = re.compile(r" ([A-Za-z]+)([, ])")
conv_equal = re.compile(r' = ')

# TBD:: support date
def toolbert_data(fname, user=None, date=None, raw=False):
    with open(fname) as f:
        for line in f:
            if line.startswith('topic = '):
                if user is not None and ' key = {},'.format(user) not in line:
                    continue
                line = line.strip()
                # value is already json formatted
                m = re.search(conv_value, line)
                line = line.replace(m.group(0), '')
                value = json.loads(m.group(1))
                line = line.replace('topic ', '"topic" ')
                line = re.sub(conv_unquoted_strings, r' "\1"\2', line)
                line = re.sub(conv_equal, r':', line)
                try:
                    js = json.loads('{'+line+'}')
                    js['value'] = value
                    if not raw:
                        clean_json(js)
                    yield js
                except:
                    print(line)
                    raise

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Convert toolbert data to jso')
    parser.add_argument('-f', '--filename', required=True, help='toolbert data filename')
    parser.add_argument('-u', '--user', type=int, help='retrieve uesr records')
    parser.add_argument('-j', '--json', action='store_true', help='output as json array')
    parser.add_argument('-r', '--raw', action='store_true', help="Don't convert string values to int, float, bool")
    args = parser.parse_args()

    if args.json:
        print(json.dumps(list(toolbert_data(args.filename, args.user, raw=args.raw)), indent=2, sort_keys=True))
    else:
        for x in toolbert_data(args.filename, args.user, raw=args.raw):
            print(json.dumps(x, indent=2, sort_keys=True))
