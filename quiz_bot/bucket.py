import boto3
import os
import json


BUCKET_NAME = 'spike-quiz-bot'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


# Yandex Object Storage Access
# OS = boto3.client(
#     's3',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name='ru-central1',
#     endpoint_url='https://storage.yandexcloud.net'
# )

def get_s3_client():
    session = boto3.session.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    return session.client(
        service_name="s3",
        endpoint_url="https://storage.yandexcloud.net"
    )


def get_image(object_name):
    s3client = get_s3_client()
    response = s3client.get_object(
        Bucket=BUCKET_NAME, Key=object_name
    )
    return response['Body'].read()
