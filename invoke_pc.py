'''
目标：批量异步调用执行lambda函数，使用invoke函数+for循环调用实现，参考链接如下：
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html#Lambda.Client.invoke
https://stackoverflow.com/questions/39456309/using-boto-to-invoke-lambda-functions-how-do-i-do-so-asynchronously
'''
import boto3
import json

client = boto3.client('lambda')

#id<18 is empty
for id in range(21,201): # 循环的范围
    payload={"id": id} # 输入id参数
    response = client.invoke(
        ClientContext='MyApp',
        FunctionName='arn:aws:lambda:us-west-2:946464008307:function:download_video', # Lambda函数的ARN名字
        InvocationType='Event', # 异步执行，会并发
        LogType='None',# 
        Payload=bytes(json.dumps(payload)),# json格式转换
        Qualifier='3', #函数版本
    )
    print response
    id = id + 1
