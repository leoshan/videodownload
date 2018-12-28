import boto3
import json
import requests
import time
import logging

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('videolist')

def filter_nones(dict):
    for key, value in dict.items():
        if value is u'':
            dict[key] = 'noname'

id = 0
for i in range(1,9207):
    REQUEST_URL="https://www.hixxxx.net/v1/videolist/?page="+bytes(i)+"&limit=12"
    r = requests.get(REQUEST_URL)
    original_json = r.json()
    response_json = original_json['response']
    videolist = response_json['videolist']

    for movie in videolist:
        filter_nones(movie)
        hip_id = movie['id']
        id_by91 = movie['id_by91']
        id_bykey = movie['id_bykey']
        duration = int(movie['duration'])
        video_name = movie['title']
        date = movie['date']
        views = movie['views']
        video_url = "https://gmqf2.hixxxx.tw/v/"+movie['id']
        download_url = "https://cdnclientNNNN.vcdn.us/download/mp4/"+movie['id_bykey']+".mp4"
        id = id + 1

        table.put_item(
            Item={
                'id': id,
                'id_bykey': id_bykey,
                'duration': duration,
                'hip_id': hip_id,
                'id_by91': id_by91,
                'video_name': video_name,
                'date': date,
                'views': views,
                'video_url': video_url,
                'download_url': download_url,
            }
        )
        LOG_FORMAT = "%(asctime)s  %(filename)s : %(levelname)s  %(message)s"
        DATE_FORMAT = "'%Y-%m-%d %A %H:%M:%S'"
        logging.basicConfig(filename='putitem.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, filemode = 'w')
        str_i=bytes(i)
        str_id=bytes(id)
        str_videoname=video_name.encode('utf-8')
        str_download=str(download_url)
        logging.info('Current Page: %s , Current id: %s ,download_url: %s, video name: %s', str_i, str_id, str_download, str_videoname)
    time.sleep(0.1)
