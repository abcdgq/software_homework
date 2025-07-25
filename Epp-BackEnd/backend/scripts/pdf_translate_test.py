
# -*- coding: utf-8 -*-
import json
import os
import sys
import uuid
import requests
import base64
import hashlib
import time

from imp import reload
reload(sys)

#sys.setdefaultencoding('utf-8')

YOUDAO_URL_UPLOAD = 'https://openapi.youdao.com/file_trans/upload'
YOUDAO_URL_QUERY = 'https://openapi.youdao.com/file_trans/query'
YOUDAO_URL_DOWNLOAD = 'https://openapi.youdao.com/file_trans/download'
APP_KEY = '3a32217d0a6b794e'
APP_SECRET = 'q70jkzoHBKk5KXdqTq0K8Epr5uvMkwBC'


def truncate(q):
    if q is None:
        return None
    q_utf8 = q.decode("utf-8")
    size = len(q_utf8)
    return q_utf8 if size <= 20 else q_utf8[0:10] + str(size) + q_utf8[size - 10:size]


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def do_request(url, data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(url, data=data, headers=headers)


def upload(pdf_path,pdf_name):
    route = pdf_path
    # route = os.path.join("D:\\software_homework\\Epp-BackEnd\\backend\scripts\\untranslated_pdf", pdf_name)
    #route = os.path.join(".\\untranslated_pdf", pdf_name)
    f = open(route, 'rb')  # 二进制方式打开文件
    q = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
    f.close()
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['q'] = q
    data['fileName'] = pdf_name
    data['fileType'] = 'pdf'
    data['langFrom'] = 'en'
    data['langTo'] = 'zh-CHS'
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_UPLOAD, data)
    print (response.content)
    return json.loads(response.content.decode("utf-8"))["flownumber"]


def query(q):
    flownumber = q
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = APP_KEY + truncate(flownumber.encode("utf-8")) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['flownumber'] = flownumber
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_QUERY, data)
    print (response.content)
    return json.loads(response.content.decode("utf-8"))["status"]

def download(q, pdf_name):
    flownumber = q
    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    signStr = APP_KEY + truncate(flownumber.encode("utf-8")) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)

    data = {}
    data['flownumber'] = flownumber
    data['downloadFileType'] = 'pdf'
    data['appKey'] = APP_KEY
    data['salt'] = salt
    data['curtime'] = curtime
    data['sign'] = sign
    data['docType'] = 'json'
    data['signType'] = 'v3'

    response = do_request(YOUDAO_URL_DOWNLOAD, data)
    #print (response.content)
    # 定义PDF保存路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    translated_dir = os.path.join(script_dir, "../scripts/translated_pdf")
    if not isinstance(pdf_name, str):
        # 假设 UserDocument 对象有一个获取文件名的属性或方法
        pdf_name = str(pdf_name)
    route = os.path.join(translated_dir, "translated__"+pdf_name+'.pdf')
    #route = os.path.join(".\\untranslated_pdf", "translated__"+pdf_name)

    # 写入文件
    with open(route, 'wb') as f:  # 'wb' 表示以二进制写入模式打开文件
        f.write(response.content)

def pdf_translate(pdf_path,pdf_name):
    q = upload(pdf_path,pdf_name)
    status = 0
    while(True):
        status = query(q)
        if(status == 4 or status < 0): break
        else: time.sleep(3)
    if status == 4:
        download(q, pdf_name)
        return True
    else: print("error:" + status)
    return False

if __name__ == '__main__':
    pdf_translate("test.pdf")