from __future__ import print_function
import wget # pip install wget
import boto3 # pip install boto3
import json
import logging
import os
from boto3.dynamodb.conditions import Key, Attr

def get_video_by_id(id):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('videolist')
    s3_client = boto3.client('s3')
    response = table.query(
        IndexName='id-video_name-index',
        KeyConditionExpression=Key('id').eq(id)
    )
    #print(response)
    if response['Items']:
        for item in response['Items']:
            #print(item)
            url = item['download_url']
            video_name = item['video_name']
            str_videoname = item['video_name']
            out_fname = "/tmp/video_"+item['id_bykey']+".mp4"
            filename = wget.download(url,out_fname)
            print('Downloaded video id is: ',id,'; filename is: ', filename)
            upload_path = filename
            key = os.environ['VIDEO_DIR']+"/video_"+item['id_bykey']+".mp4"
            '''
            p = os.popen('ls -lh /tmp',"r")
            while 1:
                line = p.readline()
                if not line:break
                print(line)
            '''
            s3_client.upload_file(upload_path, os.environ['S3_BUCKET'], key)
            print('Upload video id is: ',id,'; filename is: ', filename,'; video name is: ', str_videoname)
    else:
        print('id',id,'is not exist') 

def download_video(event,context):
    uname = os.uname()
    print(uname)
    
    p = os.popen('uptime',"r")
    while 1:
        line = p.readline()
        if not line:break
        print(line) 
    
    p = os.popen('cat /proc/meminfo|grep -E "MemTotal|MemAvailable"',"r")
    while 1:
        line = p.readline()
        if not line:break
        print(line)
    
    p = os.popen('cat /proc/cpuinfo | grep "model name"',"r")
    while 1:
        line = p.readline()
        if not line:break
        print(line)
    '''
    id = event['id']
    get_video_by_id(id)
    
    '''
    for record in event['Records']:
        #body = json.dumps(record['body'])# "{\"id\": 13371}"
        body = record['body']# body is a string, {"id": 12206}
        #print(body) # {"id": 9130}
        json_body = json.loads(body)# body is a string, so str to json
        id = json_body["id"]
        get_video_by_id(id)

