import os
import boto3
from botocore.exceptions import NoCredentialsError

'''
https://planfit-images.s3.ap-northeast-2.amazonaws.com/training-videos/2035.mp4
'''

def download_dir(client, resource, dist, local='./', bucket='planfit-images'):
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_dir(client, resource, subdir.get('Prefix'), local=local, bucket=bucket)
        for file in result.get('Contents', []):
            dest_pathname = os.path.join(local, file.get('Key'))
            if not os.path.exists(os.path.dirname(dest_pathname)):
                os.makedirs(os.path.dirname(dest_pathname))
            resource.meta.client.download_file(bucket, file.get('Key'), dest_pathname)

def main():
    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')
    download_dir(s3_client, s3_resource, 'training-videos/', '../training-videos/', bucket='planfit-images')

if __name__ == "__main__":
    main()
