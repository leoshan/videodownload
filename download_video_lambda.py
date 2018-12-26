from __future__ import print_function
import wget # pip install wget
import boto3 # pip install boto3
import json
import logging
from boto3.dynamodb.conditions import Key, Attr

def download_video(event,context):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    s3_client = boto3.client('s3')

    table = dynamodb.Table('videolist')
    id = event['id']
    response = table.query(
        IndexName='id-video_name-index',
        KeyConditionExpression=Key('id').eq(id)
    )
    for item in response['Items']:
        url = item['download_url']
        video_name = item['video_name']
        str_videoname = item['video_name']
        out_fname = "/tmp/video_"+item['id_bykey']+".mp4"
        filename = wget.download(url,out_fname)
        print('Downloaded video id is: ',bytes(id),'; filename is: ', filename)
        upload_path = filename
        key = "video1k/video_"+item['id_bykey']+".mp4"
        bucket = 'video-uw2'
        s3_client.upload_file(upload_path, bucket, key)
        print('Upload video id is: ',bytes(id),'; filename is: ', filename,'; video name is: ', str_videoname)
