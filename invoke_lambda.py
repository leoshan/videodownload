import boto3
import json

def invoke_range(start,end):
    client = boto3.client('lambda')
    #id<18 is empty
    for id in range(start,end): 
        payload={"id": id} #
        response = client.invoke(
            ClientContext='MyApp',
            FunctionName='arn:aws:lambda:us-west-2:946464008307:function:download_video',
            InvocationType='Event',
            LogType='Tail',
            Payload=bytes(json.dumps(payload)),
            Qualifier='3',
        )
        print response
        id = id + 1

def lambda_invoke(event,context):
    start = event['start']
    end = event['end']
    invoke_range(start,end)
