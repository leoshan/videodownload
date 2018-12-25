import wget # pip install wget
import boto3 # pip install boto3
import json
import logging
from boto3.dynamodb.conditions import Key, Attr # 通过id查询时使用

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('videolist')

LOG_FORMAT = "%(asctime)s  %(filename)s : %(levelname)s  %(message)s"
DATE_FORMAT = "'%Y-%m-%d %H:%M:%S'"
#日志输出的名字
logging.basicConfig(filename='download.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, filemode = 'w')

for id in range(1,100): # 循环下载
    response = table.query( # 使用query来做dynamodb表格查询，返回的是Json格式，aws configure配置的
        IndexName='id-video_name-index', # 索引的名称
        KeyConditionExpression=Key('id').eq(id) # 查询的条件，查询Key为id=1的时候的Item内容
    )
    id = id + 1
    for item in response['Items']: # 遍历dynamodb的返回结果，取出'Item'字典的内容
        url = item['download_url'] # 获取字典里面的下载链接
        out_fname = "video_"+item['id_bykey']+".mp4" # 修改原始文件名为video_+id_bykey.mp4
        filename = wget.download(url,out_fname) # 使用wget下载链接，并改成相应名字

        video_name = item['video_name']
        str_videoname = video_name.encode('utf-8') # 这两句是获取视频的名字
        str_id = bytes(id)
        str_filename = str(filename) # 这两句是转换成字符串为了日志输出

        logging.info('Current id: %s , file name: %s , video name: %s ', str_id, str_filename, str_videoname)
