
# -*- coding: utf-8 -*-
import json
import sys
import uuid
import requests
import hashlib
import time
from imp import reload

import time

reload(sys)

YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '3a32217d0a6b794e'
APP_SECRET = 'q70jkzoHBKk5KXdqTq0K8Epr5uvMkwBC'


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(sentence:str, domain="general"):
    q = sentence

    data = {}
    #data['from'] = 'en' #源语言
    #data['to'] = 'zh-CHS' #目标语言
    #不填from 和 to自动中转英 英转中
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q #待输入文字
    data['salt'] = salt #自动生成
    data['sign'] = sign #自动生成
    #TODO:用户词表项非必填，以后可扩展实现该功能，即用户自定义用户词表
    #data['vocabId'] = "您的用户词表ID"
    data['domain'] = domain

    response = do_request(data)
    contentType = response.headers['Content-Type']
    if contentType == "audio/mp3":
        millis = int(round(time.time() * 1000))
        filePath = "合成的音频存储路径" + str(millis) + ".mp3"
        fo = open(filePath, 'wb')
        fo.write(response.content)
        fo.close()
    else:
        formatted_response = json.loads(response.content.decode("utf-8"))
        print(formatted_response["translation"])
        #返回翻译好的句子
        return formatted_response["translation"] 
    

if __name__ == '__main__':
    connect("返回翻译好的句子", "game")