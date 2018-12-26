'''
目标：通过Lambda Python读取DynamoDB数据库的url，wget下载下来，上传到S3的bucket
前置知识：
1、Lambda知识：
  Lambda程序打包（pip install wget -t project-dir，在Project-dir里面选择所有文件打包zip）
  lambda角色设置（需要在基础角色上面添加daynamodb和S3的可访问控制策略）
  最佳实践，管理并发执行
  资源情况：临时磁盘/tmp 512MB，内存128MB，请求最大时长5分钟-15分钟，并发执行1000（相当于同时启动1000个下载进程）
2、python编程：在videolist里面的基础上，wget存储到指定路径（查看wget download函数源码）
3、S3知识：S3存储桶、Client上传文件到指定目录（Boto3手册查询）
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file
4、核心关键点：S3 client文件上传到指定桶、指定目录；Wget下载文件到指定路径；
  Lambda程序打包及函数处理应用，角色设置。
'''

from __future__ import print_function # print函数在Python2和Python3之间的兼容性
import wget # pip install wget
import boto3 # pip install boto3
import json
import logging
from boto3.dynamodb.conditions import Key, Attr

'''
event - AWS Lambda 使用此参数将事件数据传递到处理程序。
此参数通常是 Python dict 类型。它也可以是 list、str、int、float 或 NoneType 类型。
context - AWS Lambda 使用此参数向您的处理程序提供运行时信息。此参数为 LambdaContext 类型。
'''

def download_video(event,context): # lambda函数的固定模式，两个参数，event
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1') # 连接dynamodb数据库
    s3_client = boto3.client('s3') # 使用S3client 上传数据

    table = dynamodb.Table('videolist')
    id = event['id'] # 认为even是个字典，通过event参数获取id值
    response = table.query( # 使用query来做dynamodb表格查询，返回的是Json格式
        IndexName='id-video_name-index', # 索引的名称
        KeyConditionExpression=Key('id').eq(id) # 查询的条件，查询Key为id=1的时候的Item内容
    )
    for item in response['Items']: # 遍历dynamodb的返回结果，取出'Item'字典的内容
        #下载dynamodb中的URL，将文件写到/tmp，且改名字
        url = item['download_url'] # 获取字典里面的下载链接
        video_name = item['video_name']
        str_videoname = item['video_name'] # 获取字典里面的文件名，并转换成str
        #lambda只允许/tmp目录可以写，最大512MB；下载之后的需要更改，自己拼装文件名
        #wget要下载文件到指定路径/tmp，且要改文件名字video_xxx.mp4
        out_fname = "/tmp/video_"+item['id_bykey']+".mp4" # 文件输出路径及改名
        filename = wget.download(url,out_fname) # wget下载，输出结果是文件存储路径
        print('Downloaded video id is: ',bytes(id),'; filename is: ', filename) #打印日志
        #S3从/tmp目录将视频文件上传到所属的Bucket及指定目录
        upload_path = filename # 上传路径就是刚刚的wget下载之后的执行结果
        key = "video1k/video_"+item['id_bykey']+".mp4" # S3_client upload_file需要指定文件名video_xxx.mp4及路径video1k
        bucket = 'video-uw2' # 指定bucket
        s3_client.upload_file(upload_path, bucket, key) #S3 client上传数据
        #打印日志到cloudwatch
        print('Upload video id is: ',bytes(id),'; filename is: ', filename,'; video name is: ', str_videoname)
