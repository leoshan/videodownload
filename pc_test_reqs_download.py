#import wget # pip install wget
import requests
import boto3 # pip install boto3
import json
import logging
from boto3.dynamodb.conditions import Key, Attr


def download_video(id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('videolist')
    response = table.query(
        IndexName='id-video_name-index',
        KeyConditionExpression=Key('id').eq(id)
    )
    for item in response['Items']:
        #url = item['download_url']
        url = "https://hp.cdnbyte.top/download/mp4/"+item['id_bykey']+".mp4" # update new URL
        print(url)
        out_fname = "video_"+item['id_bykey']+".mp4"
        #filename = wget.download(url,out_fname) # where download file stor

        headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
        r = requests.get(url,stream=True,headers = headers)
        print(r)
        print(r.headers)
        #print(r.headers.get('content-disposition'))
        open(out_fname, 'wb').write(r.content)
        
download_video(83736)
