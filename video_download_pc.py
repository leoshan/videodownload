import wget # pip install wget
import boto3 # pip install boto3
import json
import logging
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('videolist')

LOG_FORMAT = "%(asctime)s  %(filename)s : %(levelname)s  %(message)s"
DATE_FORMAT = "'%Y-%m-%d %H:%M:%S'"
logging.basicConfig(filename='download.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, filemode = 'w')

for id in range(1,100):
    response = table.query(
        IndexName='id-video_name-index',
        KeyConditionExpression=Key('id').eq(id)
    )
    id = id + 1
    for item in response['Items']:
        url = item['download_url']
        out_fname = "video_"+item['id_bykey']+".mp4"
        filename = wget.download(url,out_fname)

        video_name = item['video_name']
        str_videoname = video_name.encode('utf-8')
        str_id = bytes(id)
        str_filename = str(filename)

        logging.info('Current id: %s , file name: %s , video name: %s ', str_id, str_filename, str_videoname)
