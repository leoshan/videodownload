# videodownload
Python Json DynamoDB（结构化数据存储） S3 Galicer（数据存储） Lightsail（数据传输）Lambda(批量下载)

Restful API信息抓取存储到 DynamoDB，把云计算的资源用起来

缘起于看到牛人在论坛发的一个帖子，看牛人趟路，用了周末一个下午加一个晚上写了个Python脚本，Python能力较差，全程靠Google解决问题

架构如下：

![设计架构](https://raw.githubusercontent.com/leoshan/videodownload/master/arch.png)

函数调用时间：当超过2000个并发进行下载时, 调度用时452500ms，452秒，还有一次2000并发是401秒。平均一次函数调用在220ms左右。

失败函数处理：由于aws lambda批量调用时会有未知失败，所以需要开启死信队列来保存失败信息。（可以看到失败原因为调用超时和/tmp目录已满）。调用超时原因可能是并发超过最大上限。/tmp目录已满是因为多个函数执行在一个容器里，前一个已下载的文件没有删除导致的。目录重新配置死信队列为事件触发事件，读取body中的id信息（body的返回值是个字符串”{\”Id\”: 10001}”,需要通过json.loads(body)转换成dict，然后才能调用，这个是大坑，尤其是用了print打出来的信息很有迷惑性）进行再次调用下载直到下载成功。

Amazon SQS 事件
{
     "Records": [
        {
            "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
            "receiptHandle": "AQEBJQ+/u6NsnT5t8Q/VbVxgdUl4TMKZ5FqhksRdIQvLBhwNvADoBxYSOVeCBXdnS9P+erlTtwEALHsnBXynkfPLH3BOUqmgzP25U8kl8eHzq6RAlzrSOfTO8ox9dcp6GLmW33YjO3zkq5VRYyQlJgLCiAZUpY2D4UQcE5D1Vm8RoKfbE+xtVaOctYeINjaQJ1u3mWx9T7tork3uAlOe1uyFjCWU5aPX/1OHhWCGi2EPPZj6vchNqDOJCY2k1gkivqCjz1CZl6FlZ7UVPOx3AMoszPuOYZ+Nuqpx2uCE2MHTtMHD8PVjlsWirt56oUr6JPp9aRGo6bitPIOmi4dX0FmuMKD6u/JnuZCp+AXtJVTmSHS8IXt/twsKU7A+fiMK01NtD5msNgVPoe9JbFtlGwvTQ==",
            "body": "{\"id\": 10001 }",
            "attributes": {
                "ApproximateReceiveCount": "3",
                "SentTimestamp": "1529104986221",
                "SenderId": "594035263019",
                "ApproximateFirstReceiveTimestamp": "1529104986230"
            },
            "messageAttributes": {},
            "md5OfBody": "9bb58f26192e4ba00f01e2e7b136bbd8",
            "eventSource": "aws:sqs",
            "eventSourceARN": "arn:aws:sqs:us-west-2:594035263019:NOTFIFOQUEUE",
            "awsRegion": "us-west-2"
        }
    ]
}

https://docs.aws.amazon.com/zh_cn/lambda/latest/dg/with-sqs-create-package.html

Lambda SQS example
