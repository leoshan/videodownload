'''
目的：利用python抓取Restful API输出的结果，做一些字符串内容处理，并将结果分别保存到Dynamodb和日志文件备用.
前置知识：
 1、AWS SDK使用（awscli、Boto3），安装boto3、安装AWSCLI、aws configure配置连接
 2、DynamoDB知识：创建表（主键、排序），本地Dynamodb开发测试验证，SDK 连接数据库，数据写入PutItem
 3、RestfulAPI：Postman访问，连接获取，参数使用
 4、Json知识: 对象、数组
 5、Python编程知识： RestfulAPI访问：requests，字符串拼接，数组、字典提取及引用，for循环及嵌套循环
   Json数据提取编程，变量数据类型转换，日志输出，时间延迟，字典赋值，空值替换
 6、关键问题： Json数据解析、空值替换、日志输出、双重for循环，后续考虑函数化运作
'''

'''
Postman访问https://www.xxx.net/v1/videolist/?page=7096&limit=12输出的结果如下，根据这个内容进行Json解析
想要的内容是id_bykey的value加上某个链接就可以下载视频
{
    "status": true,
    "response": {
        "total": 110508,
        "videolist": [
            {            {
                "id": "6Bv",
                "id_by91": "102579",
                "id_bykey": "ef417de581b01f918e54",
                "cid": 1,
                "title": "打电话",
                "date": "2018-02-26",
                "duration": 64,
                "status": "1",
                "rateing": 0,
                "views": 841
            },
            {
                "id": "6Bu",
                "id_by91": "102580",
                "id_bykey": "c7aaf031f6f9efd56c60",
                "cid": 1,
                "title": "家。",
                "date": "2018-02-26",
                "duration": 70,
                "status": "1",
                "rateing": 0,
                "views": 218
            }
        ]
    }
}
'''

import boto3
import json
import requests
import time
import logging

#dynamodb 连接，指定区域和表名，表创建指定主键和排序键
dynamodb = boto3.resource('dynamodb', region_name='us-east-1') #使用的是弗吉尼亚的数据库
table = dynamodb.Table('videolist') # videolist是Dynamodb的表名，按照这个实际能力选择默认的5个读写容量就够用

#空值替换函数，没有这个东东的时候，PutItem插入空值报错，为了要关键数据，所以进行空值替换
def filter_nones(dict):             #dict变量是字典{'key':'value'}的内容
    for key, value in dict.items(): #这里key, value是变量，dict.items()是以列表返回可遍历的(键, 值) 元组数组
        if value is u'':            #根据查看实际的空值是u''，所以判断value是否为空，用这句
            dict[key] = 'NoValue'   #给字典当中某个Key赋值，字符串需要单引号引起来

id = 0
#循环访问每个RestApi的界面，并把结果转换成Json，提取关键信息的数组
for i in range(1,9207): # for循环可以是用range（a,b）,取个范围，也可以是for i in [6612,6807,7096]，选择List进行
    REQUEST_URL="https://www.xxx.net/v1/videolist/?page="+bytes(i)+"&limit=12" # 字符串拼接，i是数字型的，需要bytes（）进行str转换
    r = requests.get(REQUEST_URL) # 使用requests进行获取Restfull输出内容
    original_json = r.json() # 将Request内容输出内容转换成Json格式
    response_json = original_json['response']
    videolist = response_json['videolist'] # 从字典获取videolist数组，里面的结构是{"response"：{"videolist":[{},{}]}}

#遍历视频列表数组，获取关键字段信息，为插入DynamoDb做准备
    for movie in videolist: # 遍历videolist数组，movie的内容是字典{'key1':'value1','key2':'value2'}，
        filter_nones(movie) # 空值替换
        hip_id = movie['id'] # 以下为字典内容读取，为后面putitem赋值准备，为选择全部
        id_by91 = movie['id_by91']
        id_bykey = movie['id_bykey']
        duration = int(movie['duration'])
        video_name = movie['title']
        date = movie['date']
        views = movie['views']
        video_url = "https://xxxx.xxx.tw/v/"+movie['id'] # 通过字符串拼接生成视频的url
        download_url = "https://cdnclientxxxx.vcdn.us/download/mp4/"+movie['id_bykey']+".mp4" # 通过字符串拼接生成下载视频的url，发现了url生成规律，核心就是要这个
        id = id + 1 # 生成一个id为了将来转换成Mysql和记录插入了多少条数据，为了后续与Total的值比较。

#调用AWS Dynamodb 的putitem接口插入数据，与前面的参数对应，参照样例改的。后续可以考虑BatchputItem的使用。
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
#log信息输出，两个目的：1、万一脚本执行错误，不用从0开始执行，可以接着再跑；2、输出想要的核心内容到文本文档，留作备份使用。
        LOG_FORMAT = "%(asctime)s  %(filename)s : %(levelname)s  %(message)s"
        DATE_FORMAT = "'%Y-%m-%d %A %H:%M:%S'"
        logging.basicConfig(filename='putitem.log', level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT, filemode = 'w') # 以上三行是照着网上情况来的，关键是level要选对。
#这五行是因为最后的logging.info()输出的时候，一直报错，不是str格式，不能输出。
        str_i=bytes(i)
        str_id=bytes(id) # 将简单的整形转换成str
        str_videoname=video_name.encode('utf-8') # videoname有中文字符，需要这个方式才能转换成str，普通的str()函数搞不定
        str_download=str(download_url) # 普通的英文字符，可以直接使用str()转换成str
        logging.info('Current Page: %s , Current id: %s ,download_url: %s, video name: %s', str_i, str_id, str_download, str_videoname) # 格式化输出，注意%s要和后面的输出变量相对应，注意单引号
    time.sleep(0.1) # 为了担心系统识别到是异常访问，设置0.1秒延时，也可以延迟1秒，time.sleep(1)
