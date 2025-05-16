"""
    用户上传论文相关接口
"""
import os

import PyPDF2
from backend.settings import USER_DOCUMENTS_PATH, BATCH_DOWNLOAD_PATH, BATCH_DOWNLOAD_URL
from backend.settings import USER_DOCUMENTS_URL
from business.models import User, UserDocument, FileReading
from django.http import JsonResponse
import json
import random
import time
import zipfile
from django.views.decorators.http import require_http_methods

from business.utils import reply
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


if not os.path.exists(USER_DOCUMENTS_PATH):
    os.makedirs(USER_DOCUMENTS_PATH)


def upload_paper(request):
    """
    上传文献
    """
    if request.method == 'POST':
        file = request.FILES.get('new_paper')
        username = request.session.get('username')
        user = User.objects.filter(username=username).first()
        print(file)
        print(username)
        print(request.session)
        if user and file:
            # 保存文件
            file_name = os.path.splitext(file.name)[0]
            file_ext = os.path.splitext(file.name)[1]
            store_name = file_name + time.strftime('%Y%m%d%H%M%S') + '_%d' % random.randint(0, 100) + file_ext
            file_size = file.size
            file_path = USER_DOCUMENTS_PATH + '/' + store_name
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            # 保存文献信息
            usr_document = UserDocument(user_id=user, title=file_name, local_path=file_path, format=file_ext,
                                        size=file_size)
            usr_document.save()
            file_url = USER_DOCUMENTS_URL + store_name
            return JsonResponse({'message': '上传成功', 'file_id': usr_document.document_id, 'file_url': file_url,
                                 'is_success': True})
        else:
            return JsonResponse({'error': '用户或文件不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


def remove_uploaded_paper(request):
    """
    删除上传的文献
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        username = request.session.get('username')
        document_id = data.get('paper_id')
        user = User.objects.filter(username=username).first()
        document = UserDocument.objects.filter(document_id=document_id).first()
        if user and document:
            if document.user_id == user:
                if os.path.exists(document.local_path):
                    os.remove(document.local_path)
                # else:
                #     return JsonResponse({'error': '文件不存在', 'is_success': False}, status=400)
                document.delete()
                return JsonResponse({'message': '删除成功', 'is_success': True})
            else:
                return JsonResponse({'error': '用户无权限删除该文献', 'is_success': False}, status=400)
        else:
            return JsonResponse({'error': '用户或文献不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


@require_http_methods('GET')
def document_list(request):
    """ 用户上传文件列表 """
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()
    # user = User.objects.filter(username='22371427').first()
    if not user:
        return reply.fail(msg="请先正确登录")

    print(username)
    documents = UserDocument.objects.filter(user_id=user).order_by('-upload_date')
    data = {'total': len(documents), 'documents': []}
    for document in documents:
        url = USER_DOCUMENTS_URL + os.path.basename(document.local_path)
        file_reading = FileReading.objects.filter(document_id=document.document_id).first()
        data['documents'].append({
            "document_id": document.document_id,
            "document_url": url,
            "file_reading_id": file_reading.id if file_reading else None,
            "title": document.title,
            "format": document.format,
            "size": document.size,
            "date": document.upload_date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return reply.success(data=data, msg='文件列表获取成功')


def get_document_url(request):
    """
    获取用户上传文件url
    """
    if request.method == 'GET':
        document_id = request.GET.get('document_id')
        document = UserDocument.objects.filter(document_id=document_id).first()
        if document:
            return JsonResponse(
                {'message': '获取成功', 'local_url': '/' + document.local_path,
                 'is_success': True})
        else:
            return JsonResponse({'error': '文件不存在', 'is_success': False}, status=400)
    else:
        return JsonResponse({'error': '请求方法错误', 'is_success': False}, status=400)


@require_http_methods('GET')
def download_document_translated_url(request):
    '''
    下载用户上传文档的翻译结果(pdf文件)
    '''
    document_id = request.GET.get('document_id')
    document_path = UserDocument.objects.filter(document_id=document_id).values('local_path').first().values()
    document_name = UserDocument.objects.filter(document_id=document_id).first()
    value_list = list(document_path)
    path = value_list[0]   # pdf的path
    # print(document_name)
    username = request.session.get('username')

    script_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.abspath(os.path.join(script_dir, '..\\..\\' + path))
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = len(reader.pages)
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                text = page.extract_text()
                print(text)
    except FileNotFoundError:
        print(f"文件 {pdf_path} 不存在。")
    except Exception as e:
        print(f"读取 PDF 文件时发生错误: {str(e)}")
    if pdf_path:
        # 对该论文进行翻译
        if(pdf_translate(pdf_path=pdf_path,pdf_name=document_name)) :
            if not isinstance(document_name,str):
                document_name = str(document_name)
            translated_filename = os.path.abspath(os.path.join(script_dir, '..\\..\\' + 'scripts\\translated_pdf','translated__'+document_name+'.pdf'))
        else :
            data = {
                'zip_url': '/',
                'is_success': False
            }
            return reply.fail(data=data , msg="没翻译成功")
        

        # 将所有paper打包成zip文件，存入BATCH_DOWNLOAD_PATH，返回zip文件路径
        zip_name = (username + '_batchDownload_' + time.strftime('%Y%m%d%H%M%S') +
                    '_%d' % random.randint(0, 100) + '.zip')
        zip_file_path = os.path.join(BATCH_DOWNLOAD_PATH, zip_name)
        print(zip_file_path)
        with zipfile.ZipFile(zip_file_path, 'w') as z:
            z.write(translated_filename, arcname=os.path.basename(translated_filename))

        zip_url = BATCH_DOWNLOAD_URL + zip_name

        data = {
            'zip_url': zip_url,
            'is_success': True
        }
        return reply.success(data=data, msg="成功翻译并下载翻译结果")

    else:
        data = {
            'zip_url': '/',
            'is_success': False
        }
        return reply.fail(data=data , msg="找不到需要翻译的论文")

def get_translate_pdf(directory):
    # 获取当前脚本的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 将用户提供的目录与脚本目录拼接，并解析为规范化的绝对路径
    target_dir = os.path.abspath(os.path.join(script_dir, '..\\..' + directory))
    # print(target_dir)

    # 获取目录下所有条目
    all_files = os.listdir(target_dir)
    # print(all_files)

    # 过滤出PDF文件（不区分大小写）
    pdf_files = [
        f for f in all_files
        if os.path.isfile(os.path.join(target_dir, f)) and f.lower().endswith('.pdf')
    ]

    if not pdf_files:
        raise FileNotFoundError(f"未找到PDF文件，目录：{target_dir}")

    return target_dir + '\\' + random.choice(pdf_files)
    # return random.choice(pdf_files)

# translated_filename = get_random_pdf('/resource/database/papers')
# print(translated_filename)


# -*- coding: utf-8 -*-


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
    translated_dir = os.path.join(script_dir, "..\\..\\scripts\\translated_pdf")
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