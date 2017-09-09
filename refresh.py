from io import BytesIO
import boto3
import requests
import os


def handler(event, context):
    get_response = requests.get(os.environ['source_url'])

    print get_response

    s3 = boto3.client('s3')
    response = s3.upload_fileobj(BytesIO(get_response.content), os.environ['s3_bucket'], os.environ['s3_key'])
    print response

    if response:
        raise Exception()

    return 'success'

if __name__ == '__main__':
    os.environ['source_url'] = 'https://data.texas.gov/download/rmk2-acnw/application%2Foctet-stream'
    os.environ['s3_bucket'] = 'austin-transit'
    os.environ['s3_key'] = 'tripupdates.pb'
    print(handler(None, None))
