#!/usr/bin/env python

import boto3
import botocore
from argparse import ArgumentParser
import sys, os
import json

# COS bucket names should be lowercase, no underscores

class CloudObjectStore(object):
    def __init__(self, credentials, bucket):
        self.credentials = credentials
        self.bucket = bucket
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=credentials['aws_access_key_id'],
                                      aws_secret_access_key=credentials['aws_secret_access_key'],
                                      endpoint_url=credentials['endpoint_url'])

    def list_objects(self):
        # TBD: handle >1000 objects
        rval = []
        js = self.s3_client.list_objects(Bucket=self.bucket)
        for item in js.get('Contents', []):
            rval.append({ 'name': item['Key'], 'size': item['Size'] })
        return rval

    def delete_object(self, object_name):
        self.s3_client.delete_object(Bucket=self.bucket, Key=object_name)

    def download_object(self, object_name, local_name=None):
        if local_name is None:
            local_name = object_name
        self.s3_client.download_file(self.bucket, object_name, local_name)

    def upload_object(self, local_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(local_name)
        self.s3_client.upload_file(local_name, self.bucket, object_name)

    def list_buckets(self):
        return self.s3_client.list_buckets()['Buckets']

def cos_list(osr, args):
    files = osr.list_objects()
    for file in sorted(files, key = lambda f: f['name']):
        print('{} ({})'.format(file['name'], file['size']))

def cos_download(osr, args):
    osr.download_object(args.objectname, args.filename)

def cos_upload(osr, args):
    osr.upload_object(args.filename, args.objectname)

def cos_delete(osr, args):
    osr.delete_object(args.objectname)

def cos_listbuckets(osr, args):
    for bucket in osr.list_buckets():
        print(bucket['Name'])

if __name__ == "__main__":
    parser = ArgumentParser(description='Cloud object storage utility tool')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-c', '--credfile', required=True, help='COS json credentials (w/ HMAC key)')
    required.add_argument('-b', '--bucket', required=True, help='COS bucket name (ignored for listbuckets)')

    subparsers = parser.add_subparsers(dest='command', help='Commands')
    download_parser = subparsers.add_parser('download', help='Download from COS')
    download_parser.add_argument('objectname', help='COS object name')
    download_parser.add_argument('-f', '--filename', help='local filename')
    download_parser.set_defaults(func=cos_download)

    listbuckets_parser = subparsers.add_parser('listbuckets', help='List buckets in COS')
    listbuckets_parser.set_defaults(func=cos_listbuckets)

    upload_parser = subparsers.add_parser('upload', help='Upload to COS')
    upload_parser.add_argument('filename', help='COS object name')
    upload_parser.add_argument('-o', '--objectname', help='COS objectname')
    upload_parser.set_defaults(func=cos_upload)

    delete_parser = subparsers.add_parser('delete', help='Delete COS object')
    delete_parser.add_argument('objectname', help='COS object name')
    delete_parser.set_defaults(func=cos_delete)

    list_parser = subparsers.add_parser('list', help='List COS objects')
    list_parser.set_defaults(func=cos_list)
    args = parser.parse_args()

    with open(args.credfile) as cf:
        creds = json.load(cf)
        
    objectstore_credentials = {
        'aws_access_key_id': creds['cos_hmac_keys']['access_key_id'],
        'aws_secret_access_key': creds['cos_hmac_keys']['secret_access_key'],
        'endpoint_url': 'https://s3.us-south.cloud-object-storage.appdomain.cloud'
    }    
    objectstore_bucket = args.bucket
    osr = CloudObjectStore(objectstore_credentials, objectstore_bucket)
    
    try:
        func = args.func
    except AttributeError:
        parser.print_help()
        sys.exit(1)

    args.func(osr, args)
