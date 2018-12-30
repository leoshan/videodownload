from __future__ import print_function
import wget # pip install wget
import boto3 # pip install boto3
import json
import logging
import os
from boto3.dynamodb.conditions import Key, Attr

def download_video(event,context):
    #system info
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
    
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    s3_client = boto3.client('s3')

    table = dynamodb.Table('videolist')
    #id = event['Records']['body']['id'] #DLQ queue id  
    id = event['id'] # get id input
    response = table.query(
        IndexName='id-video_name-index',
        KeyConditionExpression=Key('id').eq(id)
    )
    #print(response)
    if response['Items']: #if id is not none
        for item in response['Items']:
            #print(item)
            url = item['download_url']
            video_name = item['video_name']
            str_videoname = video_name.encode('utf-8') # logging string need encode,print use video_name
            out_fname = "/tmp/video_"+item['id_bykey']+".mp4" #download to dest dir and change file name
            filename = wget.download(url,out_fname)
            print('Downloaded video id is: ',bytes(id),'; filename is: ', filename)
            upload_path = filename
            key = os.environ['VIDEO_DIR']+"/video_"+item['id_bykey']+".mp4" # call environment variable
            # debug /tmp dir no space
            p = os.popen('ls -lh /tmp',"r")
            while 1:
                line = p.readline()
                if not line:break
                print(line)
        
            s3_client.upload_file(upload_path, os.environ['S3_BUCKET'], key)
            print('Upload video id is: ',bytes(id),'; filename is: ', filename,'; video name is: ', str_videoname)
    else:
        print('id',bytes(id),'is not exist') 
