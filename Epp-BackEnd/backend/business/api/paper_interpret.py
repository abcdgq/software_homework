"""
本文件的功能是文献阅读助手，给定一篇文章进行阅读，根据问题的答案进行回答。
API格式如下：
api/peper_interpret/...
"""
import asyncio
import json
import os
import re
from urllib.parse import quote
import requests
from django.views.decorators.http import require_http_methods

from django.conf import settings
from business.models import UserDocument, FileReading, Paper, User
from business.utils import reply

from business.utils.download_paper import downloadPaper

# 论文研读模块

'''
    创建文献研读对话：
        上传一个文件，开启一个研读对话，返回 tmp_kb_id
    
    对话记录方式为: [
        {"role": "user", "content": "我们来玩成语接龙，我先来，生龙活虎"},
        {"role": "assistant", "content": "虎头虎脑"},
    ]
'''


def create_content_disposition(filename):
    """构建适用于Content-Disposition的filename和filename*参数"""
    # URL 编码文件名
    safe_filename = quote(filename)
    # 构建Content-Disposition头部
    disposition = f'form-data; name="file"; filename="{filename}"; filename*=UTF-8\'\'{safe_filename}'
    return disposition


# 删除Tmp_kb的缓存，用于某tmp_kb_id再也不被使用时，避免内存爆炸
def delete_tmp_kb(tmp_kb_id):
    delete_tmp_kb_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/delete_temp_docs'
    # headers = {
    #     'Content-Type': 'application/x-www-form-urlencoded'
    # }
    payload = {
        "knowledge_id": tmp_kb_id
    }
    response = requests.post(delete_tmp_kb_url, data=payload)  # data默认是form形式
    if response.status_code == 200:
        return True
    else:
        return False


# 建立file_reading和tmp_kb的映射
def insert_file_2_kb(file_reading_id, tmp_kb_id):
    # 调试：检查文件路径是否存在
    print(f"检查文件路径：{settings.USER_READ_MAP_PATH}")
    if not os.path.exists(settings.USER_READ_MAP_PATH):
        print(f"文件 {settings.USER_READ_MAP_PATH} 不存在，正在创建新文件。")
        # 创建新文件并写入空的 JSON 对象
        with open(settings.USER_READ_MAP_PATH, "w") as f:
            json.dump({}, f, indent=4)
        print(f"已成功创建新文件：{settings.USER_READ_MAP_PATH}")
        
    with open(settings.USER_READ_MAP_PATH, "r") as f:
        f_2_kb_map = json.load(f)
    if file_reading_id in f_2_kb_map:
        if delete_tmp_kb(f_2_kb_map[file_reading_id]):
            print("删除TmpKb成功")
        else:
            print("删除TmpKb失败")

    f_2_kb_map[file_reading_id] = tmp_kb_id
    with open(settings.USER_READ_MAP_PATH, "w") as f:
        json.dump(f_2_kb_map, f, indent=4)


def get_tmp_kb_id(file_reading_id):
    with open(settings.USER_READ_MAP_PATH, "r") as f:
        f_2_kb_map = json.load(f)
    # print(f_2_kb_map)
    if str(file_reading_id) in f_2_kb_map:
        return f_2_kb_map[str(file_reading_id)]
    else:
        return None


@require_http_methods(["POST"])
def create_paper_study(request):
    # 鉴权
    username = request.session.get('username')
    print(request.session)
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!username: {username}")
    if username is None:
        username = 'sanyuba'
    print(username)
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    # 处理请求头
    request_data = json.loads(request.body)
    file_type = request_data.get("file_type")  # 1代表上传文献研读, 2代表已有文件研读
    title, content_type, local_path, file_reading = None, None, None, None
    if file_type == 1:
        document_id = request_data.get("document_id")
        # 获取文件, 后续支持直接对8k篇论文进行检索
        document = UserDocument.objects.get(document_id=document_id)
        # 获取服务器本地的path
        local_path = document.local_path
        content_type = document.format
        title = document.title
        print("doc title: ", title)
        # 先查找数据库是否有对应的Filereading
        file_readings = FileReading.objects.filter(document_id=document_id)
        if file_readings.count() == 0:
            # 创建一段新的filereading对话, 并设置conversation对话路径，创建json文件
            file_reading = FileReading(user_id=user, document_id=document, title="上传论文研读",
                                       conversation_path=None)
        elif file_readings.count() >= 1:
            file_reading = file_readings.first()
        else:
            return reply.fail(msg="一个用户上传文件存在多个文献研读文件，逻辑有误")
    elif file_type == 2:
        paper_id = request_data.get("paper_id")
        paper = Paper.objects.get(paper_id=paper_id)
        title = paper.title
        content_type = '.pdf'
        local_path = get_paper_local_url(paper)
        if local_path is None:
            return reply.fail(msg="论文无法下载，请联系管理员/换一篇文章研读")
        file_reading = FileReading(user_id=user, paper_id=paper, title="数据库论文研读",
                                   conversation_path=None)
    else:
        return reply.fail(msg="类型有误, 金哥我阐述你的梦")

    file_reading.save()
    conversation_path = os.path.join(settings.USER_READ_CONSERVATION_PATH, str(file_reading.id) + ".json")
    file_reading.conversation_path = conversation_path
    file_reading.save()
    # if os.path.exists(conversation_path):
    #     os.remove(conversation_path)

    # 此时不存在记录，创建新的
    if not os.path.exists(conversation_path):
        with open(conversation_path, 'w') as f:
            json.dump({"conversation": []}, f, indent=4)

    with open(conversation_path, 'r') as f:
        history = json.load(f)

    # 上传到远端服务器, 创建新的临时知识库
    upload_temp_docs_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/upload_temp_docs'

    print("paper local path: ", local_path)
    print(open(local_path, 'rb'))
    files = [
        ('files', (title + content_type, open(local_path, 'rb'),
                   'application/vnd.openxmlformats-officedocument.presentationml.presentation'))
    ]

    # headers = {
    #     'Content-Type': 'multipart/form-data'
    # }

    response = requests.request("POST", upload_temp_docs_url, files=files)
    # 关闭文件，防止内存泄露
    for k, v in files:
        v[1].close()

    if response.status_code == 200:
        tmp_kb_id = response.json()['data']['id']
        print(f"create_tmp_kb_id: {tmp_kb_id}")
        insert_file_2_kb(str(file_reading.id), tmp_kb_id)
        return reply.success({'file_reading_id': file_reading.id, "conversation_history": history}, msg="开启文献研读对话成功")
    else:
        return reply.fail(msg="连接模型服务器失败")


'''
    恢复文献研读对话：
        传入文献研读对话id即可
'''


@require_http_methods(["POST"])
def restore_paper_study(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    # 获取filereading与文件路径，重新上传给服务器开启对话
    request_data = json.loads(request.body)
    file_reading_id = request_data.get('file_reading_id')
    fr = FileReading.objects.get(id=file_reading_id)
    if not fr.document_id:
        print("type1")
        paper = Paper.objects.get(paper_id=fr.paper_id.get_paper_id())
        local_path = paper.local_path
        title = paper.title
        content_type = ".pdf"
    else:
        print("type2")
        document = UserDocument.objects.get(document_id=fr.document_id.get_document_id())
        local_path = document.local_path
        title = document.title
        content_type = document.format

    if local_path is None or title is None:
        print("type3")
        return reply.fail(msg="服务器内无本地文件, 请检查")

    # 上传到远端服务器, 创建新的临时知识库
    upload_temp_docs_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/knowledge_base/upload_temp_docs'
    files = [
        ('files', (title + content_type, open(local_path, 'rb'),
                   'application/vnd.openxmlformats-officedocument.presentationml.presentation'))
    ]

    # headers = {
    #     'Content-Type': 'multipart/form-data'
    # }

    response = requests.request("POST", upload_temp_docs_url, files=files)
    # 关闭文件，防止内存泄露
    for k, v in files:
        v[1].close()

    # 返回结果, 需要将历史对话一起返回
    if response.status_code == 200:
        tmp_kb_id = response.json()['data']['id']
        insert_file_2_kb(str(file_reading_id), tmp_kb_id)
        # 若删除过历史对话, 则再创建一个文件
        if not os.path.exists(fr.conversation_path):
            with open(fr.conversation_path, 'w') as f:
                json.dump({"conversation": []}, f, indent=4)

        # 读取历史对话记录
        with open(fr.conversation_path, 'r') as f:
            conversation_history = json.load(f)  # 使用 json.load() 方法将 JSON 数据转换为字典

        # print("error1")

        return reply.success(
            {'file_reading_id': file_reading_id, 'conversation_history': conversation_history},
            msg="恢复文献研读对话成功")
    else:
        print("type4")
        return reply.fail(msg="连接模型服务器失败")


'''
    异步测试
'''


@require_http_methods(["POST"])
async def async_test(request):
    print("Task started.")
    await asyncio.sleep(5)  # 模拟异步操作，例如等待 I/O
    print("Task completed.")


'''
    获取本地url
'''


def get_paper_local_url(paper):
    local_path = paper.local_path
    print("get url: ", local_path)
    print("ori url: ", paper.original_url)

    original_url = paper.original_url
    # 将路径中的abs修改为pdf
    original_url = original_url.replace('abs', 'pdf')
    # 访问url，下载文献到服务器
    filename = str(paper.paper_id)
    print("开始下载")
    local_path = downloadPaper(original_url, filename)
    print("下载完成")
    paper.local_path = local_path
    paper.save()

    # if not local_path:
    #     print("local path is None")
    #     original_url = paper.original_url
    #     # 将路径中的abs修改为pdf
    #     original_url = original_url.replace('abs', 'pdf')
    #     # 访问url，下载文献到服务器
    #     filename = str(paper.paper_id)
    #     local_path = downloadPaper(original_url, filename)
    #     paper.local_path = local_path
    #     paper.save()
    return local_path


'''
    获取文献本地url, 无则下载
'''


def get_paper_url(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    paper_id = request.GET.get('paper_id')
    paper = Paper.objects.get(paper_id=paper_id)
    print('title:' + paper.title)
    paper_local_url = get_paper_local_url(paper)
    print('local_url:' + paper_local_url)
    if paper_local_url is None:
        print('文献下载失败，请检查网络或联系管理员')
        return reply.fail(msg="文献下载失败，请检查网络或联系管理员")
    return reply.success({"local_url": "/" + paper_local_url}, msg="success")


# def do_file_chat(conversation_history, query, tmp_kb_id):
#     # 将历史记录与本次对话发送给服务器, 获取对话结果
#     file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     if len(conversation_history) != 0:
#         # 有问题
#         payload = json.dumps({
#             "query": query,
#             "knowledge_id": tmp_kb_id,
#             "history": conversation_history[-10:],  # 传10条历史记录
#             "prompt_name": "text"  # 使用历史记录对话模式
#         })

#     else:
#         payload = json.dumps({
#             "query": query,
#             "knowledge_id": tmp_kb_id,
#             "prompt_name": "default"  # 使用普通对话模式
#         })
#         # print(payload)

#     def _get_ai_reply(payload):
#         response = requests.request("POST", file_chat_url, data=payload, headers=headers, stream=False)
#         ai_reply = ""
#         origin_docs = []
#         # print(response)
#         for line in response.iter_lines():
#             if line:
#                 decoded_line = line.decode('utf-8')
#                 if decoded_line.startswith('data'):
#                     data = decoded_line.replace('data: ', '')
#                     data = json.loads(data)
#                     ai_reply += data["answer"]
#                     for doc in data["docs"]:
#                         doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
#                         origin_docs.append(doc)
#         return ai_reply, origin_docs

#     # task = asyncio.create_task(_get_ai_reply())  # 创建任务
#     ai_reply, origin_docs = _get_ai_reply(payload)

#     # 给出用户仍可能存在的问题
#     def _get_prob_paper_study_question():

#         # empty模板不含任何知识库信息
#         payload = json.dumps({
#             "query": query,
#             "knowledge_id": tmp_kb_id,
#             "history": conversation_history[-4:],
#             "prompt_name": "question",  # 使用问题模式
#             "max_tokens": 50,
#             "temperature": 0.4
#         })
#         question_reply, _ = _get_ai_reply(payload)
#         question_reply = re.sub(r'\d. ', '', question_reply).split("\n")[:2]
#         question_reply.append("告诉我更多")
#         return question_reply

#     question_reply = _get_prob_paper_study_question()
#     return ai_reply, origin_docs, question_reply

import json
import requests
import re

def do_file_chat(conversation_history, query, tmp_kb_id):
    print("do_file_chat")
    file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
    headers = {
        'Content-Type': 'application/json'
    }

    # 构建请求 payload
    if len(conversation_history) != 0:
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "history": conversation_history[-10:],  # 传10条历史记录
            "prompt_name": "text",  # 使用历史记录对话模式
            "max_tokens": 500,
        })
    else:
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "prompt_name": "default",  # 使用普通对话模式
            "max_tokens": 500,
        })

    # print(f"Sending payload to server: {payload}")

    def _get_ai_reply(payload):
        try:
            # 发送请求
            response = requests.post(file_chat_url, data=payload, headers=headers, stream=True)
            # 检查 HTTP 请求是否成功
            response.raise_for_status()

            ai_reply = ""
            origin_docs = []

            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    # print(f"Received line: {decoded_line}")

                    if decoded_line.startswith('data'):
                        data = decoded_line.replace('data: ', '')
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse JSON: {e}")
                            print(f"Invalid JSON data: {data}")
                            raise

                        ai_reply += data.get("answer", "")
                        for doc in data.get("docs", []):
                            doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
                            origin_docs.append(doc)

            return ai_reply, origin_docs

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            print(f"Response status code: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Response content: {response.content if 'response' in locals() else 'N/A'}")
            raise
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    try:
        ai_reply, origin_docs = _get_ai_reply(payload)
    except Exception as e:
        print(f"Failed to get AI reply: {e}")
        raise

    def _get_prob_paper_study_question():
        payload = json.dumps({
            "query": query,
            "knowledge_id": tmp_kb_id,
            "history": conversation_history[-4:],
            "prompt_name": "question",  # 使用问题模式
            "max_tokens": 50,
            "temperature": 0.4
        })

        # print(f"Sending question payload to server: {payload}")

        try:
            question_reply, _ = _get_ai_reply(payload)
            # question_reply = question_reply.replace("\n\n", "\n")   # 避免两次换行
            question_reply = re.sub(r'\d. ', '', question_reply).split("\n")[:2]
            question_reply.append("告诉我更多")
            return question_reply
        except Exception as e:
            print(f"Failed to get study question: {e}")
            raise

    try:
        question_reply = _get_prob_paper_study_question()
    except Exception as e:
        print(f"Failed to generate study questions: {e}")
        question_reply = ["发生错误，请稍后再试", "告诉我更多"]

    return ai_reply, origin_docs, question_reply


def add_conversation_history(conversation_history, query, ai_reply, conversation_path):
    # 添加历史记录并保存
    conversation_history.extend([{
        "role": "user",
        "content": query
    }, {
        "role": "assistant",
        "content": ai_reply if ai_reply != "" else "此问题由于某原因无回答"
    }])

    with open(conversation_path, 'w') as f:
        json.dump({"conversation": conversation_history}, f, indent=4)


'''
    论文研读 Key! 此时AI回复为非流式输出, 可能浪费时间, alpha版本先这样
'''


# @require_http_methods(["POST"])
# def do_paper_study(request):
#     # 鉴权
#     username = request.session.get('username')
#     if username is None:
#         username = 'sanyuba'
#     user = User.objects.filter(username=username).first()
#     if user is None:
#         return reply.fail(msg="请先正确登录")

#     request_data = json.loads(request.body)
#     query = request_data.get('query')  # 本次询问对话
#     file_reading_id = request_data.get('file_reading_id')
#     fr = FileReading.objects.get(id=file_reading_id)
#     tmp_kb_id = get_tmp_kb_id(file_reading_id=file_reading_id)  # 临时知识库id
#     if tmp_kb_id is None:
#         return reply.fail(msg="请先创建研读会话")
#     # 加载历史记录
#     with open(fr.conversation_path, 'r') as f:
#         conversation_history = json.load(f)

#     print(tmp_kb_id)
#     conversation_history = list(conversation_history.get('conversation'))  # List[Dict]
#     # print(conversation_history, query, tmp_kb_id)
#     ai_reply, origin_docs, question_reply = do_file_chat(conversation_history, query, tmp_kb_id)
#     add_conversation_history(conversation_history, query, ai_reply, fr.conversation_path)
#     return reply.success({"ai_reply": ai_reply, "docs": origin_docs, "prob_question": question_reply}, msg="成功")

def get_final_answer(conversation_history, query, tmp_kb_id, title=None):
    # 分发
    from scripts.routing_agent import generate_subtasks,get_expert_weights
    q_type, subtasks = generate_subtasks(query)
    print("多智能体：完成子问题生成")
    print(q_type, subtasks)

    print("多智能体：开始问题分发")
    if q_type == "other":
        print("other type")
        # llm
        return do_file_chat(conversation_history, query, tmp_kb_id)
    else:
        # # api
        # api_query = subtasks.get("api")
        # api_reply = ''
        # api_reply, docs_from_api = get_api_reply(api_query)
        # print(api_reply)
        # print("多智能体：已获取api专家回答")

        # # search
        # search_query = subtasks.get("search")
        # search_reply = ''
        # search_reply, docs_from_search = get_search_reply(search_query)
        # print(search_reply)
        # print("多智能体：已获取搜索引擎专家回答")

        # # llm
        # llm_query = subtasks.get("llm")
        # print(conversation_history)
        # llm_reply, origin_docs, question_reply = do_file_chat(conversation_history, llm_query, tmp_kb_id)
        # print(llm_reply)
        # print("多智能体：已获取原生LLM专家回答")

        api_reply, docs_from_api,search_reply, docs_from_search,llm_reply, origin_docs, question_reply  = threee_api_answer(conversation_history, tmp_kb_id, subtasks)

    # 整合
    from scripts.gennerate_result import aggregate_answers
    weight = get_expert_weights(q_type)
    ai_reply = aggregate_answers(query, weight, api_reply, search_reply, llm_reply)    # 整合多专家回答
    print("多智能体：已完成问题整合")

    # 整合docs  
    for doc in docs_from_api: #规范docs格式
        origin_docs.append(" " + doc)
    for doc in docs_from_search: #规范docs格式
        origin_docs.append(" " + doc)
    docs = origin_docs
    print(origin_docs)
    # doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
    # docs.append(doc)
    print("多智能体：已完成来源整合")

    return ai_reply, docs, question_reply

def get_api_reply(api_auery):#获取本地RAG以及google scholar api检索文献结果（google scholar api有使用限制，还是以本地RAG为主）
    from scripts.test_classifyAndGenerate1 import test_localvdb_and_scholarapi #先从scripts里import，之后要把这个文件中的方法移到utils里
    return test_localvdb_and_scholarapi(api_auery)

def get_search_reply(search_query): #获取tavily搜索引擎专家的结果
    from scripts.tavily_test import tavily_advanced_search #先从scripts里import，之后要把tavily这个文件移到utils里
    qa_list = tavily_advanced_search(search_query).get("results")
    uselist = []
    times = 0
    while True: #防止产生的结果过长，导致后边没法喂给大模型进行整合，进行一下筛选
        if times > 5: #防止问太多遍
            break
        for qa in qa_list:
            if qa['raw_content']:
                if(len(qa['raw_content']) < 2000):
                    uselist.append(qa)
            else:
                if(len(qa['content']) < 2000):
                    uselist.append(qa)
        if len(uselist) >= 2:
            break
        else: #数量不够就重新问，重新筛
            qa_list = tavily_advanced_search(search_query + "len < 2000").get("results")
            uselist = []

    search_reply = "\n".join([
        f"- [{qa['title']}] {(qa['content'] if qa['raw_content'] == None else qa['raw_content'])} score ：{qa['score']}"
        for qa in uselist
        ])
    
    from scripts.text_summary import text_summarizer #对搜索引擎专家产生的结果进行总结
    summarized_search_reply = text_summarizer(search_reply)

    docs = []
    for qa in uselist:
        docs.append(qa['title'] + "   "+ qa['url'])
    #返回示例  ['VQ-VAE Explained - Papers With Code   https://paperswithcode.com/method/vq-vae', 
    # 'PDF   https://xnought.github.io/files/vq_vae_explainer.pdf']

    return summarized_search_reply, docs

import concurrent.futures
import time
# 定义获取API回复的函数
def fetch_api_reply(api_query):
    if not api_query:
        return '', []
    
    # 调用实际的API函数
    api_reply, docs_from_api = get_api_reply(api_query)
    print(api_reply)
    print("多智能体：已获取API专家回答")
    return api_reply, docs_from_api

# 定义获取搜索引擎回复的函数
def fetch_search_reply(search_query):
    if not search_query:
        return '', []
    
    # 调用实际的搜索函数
    search_reply, docs_from_search = get_search_reply(search_query)
    print(search_reply)
    print("多智能体：已获取搜索引擎专家回答")
    return search_reply, docs_from_search

# 定义获取LLM回复的函数
def fetch_llm_reply(conversation_history, llm_query, tmp_kb_id):
    if not llm_query:
        return '', [], []
    
    print(f"会话历史: {conversation_history}")
    
    # 调用实际的LLM函数
    llm_reply, origin_docs, question_reply = do_file_chat(conversation_history, llm_query, tmp_kb_id)
    print(llm_reply)
    print("多智能体：已获取原生LLM专家回答")
    return llm_reply, origin_docs, question_reply

# 添加main函数作为入口点
def threee_api_answer(conversation_history, tmp_kb_id, subtasks):
    # 使用多线程执行三个任务
    start_time = time.time()  # 记录开始时间
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 提交API任务
        api_future = executor.submit(fetch_api_reply, subtasks.get("api"))
        
        # 提交搜索任务
        search_future = executor.submit(fetch_search_reply, subtasks.get("search"))
        
        # 提交LLM任务
        llm_future = executor.submit(fetch_llm_reply, 
                                     conversation_history, 
                                     subtasks.get("llm"), 
                                     tmp_kb_id)
        
        # 获取API结果
        api_reply, docs_from_api = api_future.result()
        
        # 获取搜索结果
        search_reply, docs_from_search = search_future.result()
        
        # 获取LLM结果
        llm_reply, origin_docs, question_reply = llm_future.result()
    
    end_time = time.time()  # 记录结束时间
    
    # 打印最终结果
    print(f"\n==== 最终结果（总耗时: {end_time - start_time:.2f}秒） ====")
    print("API回复:", api_reply)
    print("搜索回复:", search_reply)
    print("LLM回复:", llm_reply)
    print("\n引用文档:")
    print("API:", docs_from_api)
    print("搜索:", docs_from_search)
    print("LLM:", origin_docs)
    print("\n建议后续问题:")
    for idx, question in enumerate(question_reply, 1):
        print(f"{idx}. {question}")
    return api_reply, docs_from_api,search_reply, docs_from_search,llm_reply, origin_docs, question_reply

@require_http_methods(["POST"])
def do_paper_study(request):
    # 调试：打印请求信息
    # print(f"请求方法: {request.method}")
    # print(f"请求路径: {request.path}")
    # print(f"请求查询参数: {request.GET}")
    # print(f"请求体: {request.body}")

    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()

    if user is None:
        return reply.fail(msg="请先正确登录")

    try:
        # 解析请求体
        request_data = json.loads(request.body)
        print(f"解析后的请求体: {request_data}")

        query = request_data.get('query')  # 本次询问对话
        print(f"获取的查询内容: {query}")

        file_reading_id = request_data.get('file_reading_id')
        print(f"获取的 file_reading_id: {file_reading_id}")

        # 查询 FileReading 对象
        fr = FileReading.objects.get(id=file_reading_id)
        print(f"查询到的 FileReading 对象: {fr}")
        # print("doc id: ", fr.document_id)
        # print("paper id: ",fr.paper_id)

        # 获取临时知识库 ID
        tmp_kb_id = get_tmp_kb_id(file_reading_id=file_reading_id)  # 临时知识库id
        print(f"获取的临时知识库 ID: {tmp_kb_id}")

        if tmp_kb_id is None:
            print("未获取到临时知识库 ID，返回失败响应")
            return reply.fail(msg="请先创建研读会话")

        # 加载历史记录
        print(f"加载对话历史文件路径: {fr.conversation_path}")
        with open(fr.conversation_path, 'r') as f:
            conversation_history = json.load(f)
        # print(f"加载的对话历史: {conversation_history}")

        conversation_history = list(conversation_history.get('conversation'))  # List[Dict]
        # print(f"转换后的对话历史: {conversation_history}")

        # 调用 AI 聊天函数
        # print(f"调用 do_file_chat，参数: conversation_history={conversation_history}, query={query}, tmp_kb_id={tmp_kb_id}")
        # ai_reply, origin_docs, question_reply = do_file_chat(conversation_history, query, tmp_kb_id)
        
        # 获取title
        title = fr.document_id if fr.document_id else fr.paper_id
        print("paper title: ", title)
        ai_reply, origin_docs, question_reply = get_final_answer(conversation_history, query, tmp_kb_id, title)

        print(f"AI 回复: {ai_reply}")
        print(f"原始文档: {origin_docs}")
        print(f"问题回复: {question_reply}")

        # 添加对话历史
        print(f"添加对话历史，路径: {fr.conversation_path}")
        add_conversation_history(conversation_history, query, ai_reply, fr.conversation_path)
        print("对话历史已添加")

        #TODO:
        from scripts.get_keywords import get_keywords
        words = get_keywords(ai_reply)

        # 返回成功响应
        print("返回成功响应")
        return reply.success({"ai_reply": ai_reply, "docs": origin_docs, "prob_question": question_reply}, msg="成功")

    except Exception as e:
        print(f"发生错误: {e}")
        # 可以选择记录错误日志或返回失败响应
        return reply.fail(msg=f"服务器内部错误: {str(e)}")


'''
    论文研读：重新生成回复
        
'''


@require_http_methods(["POST"])
def re_do_paper_study(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    request_data = json.loads(request.body)
    file_reading_id = request_data.get('file_reading_id')
    tmp_kb_id = get_tmp_kb_id(file_reading_id=file_reading_id)
    if tmp_kb_id is None:
        return reply.fail(msg="请先创建研读会话")

    fr = FileReading.objects.get(id=file_reading_id)
    conversation_path = fr.conversation_path
    with open(fr.conversation_path, 'r') as f:
        conversation_history = json.load(f)

    conversation_history = list(conversation_history.get('conversation'))
    if len(conversation_history) < 2:
        return reply.fail(msg="无法找到您的上一条对话")
    # 获取最后一次的询问, 并去除最后一次的对话记录
    query = conversation_history[-2].get('content')
    conversation_history = conversation_history[:-2]

    # 同 do_paper_study
    ai_reply, origin_docs, question_reply = do_file_chat(conversation_history, query, tmp_kb_id)
    add_conversation_history(conversation_history, query, ai_reply, conversation_path)
    return reply.success({"ai_reply": ai_reply, "docs": origin_docs, "prob_question": question_reply}, msg="成功")


# @require_http_methods(["POST"])
# def paper_interpret(request):
#     # mark:已被放弃
#     '''
#     本文件唯一的接口，类型为POST
#     根据用户的问题，返回一个回答
#     思路如下：
#         1. 根据session获得用户的username, request中包含local_path和question
#         2. 根据paper_id得到向量库中各段落的向量，根据question得到问题的向量，选择最相似的段落
#         3. 将段落输入到ChatGLM2-6B中，得到回答，进行总结，给出一个本文中的回答
#         4. 查找与其相似度最高的几篇文章的段落，相似度最高的5个段落，对每段给出一个简单的总结。
#         5. 将几个总结和回答拼接返回
#         6. 把聊天记录保存到数据库中，见backend/business/models/file_reading.py
#     return : {
#         content: str
#     }
#     '''
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         local_path = data['local_path']
#         question = data['question']
#         username = request.session.get('username')
#         user = User.objects.get(username=username)
#         file = FileReading.objects.get(user_id=user, file_local_path=local_path)
#         conversation = []
#         conversation_path = ''
#         if file is None:
#             # 新建一个研读记录
#             t = get_pdf_title(local_path)
#             file = FileReading(user_id=user.user_id, file_local_path=local_path, title=t, conversation_path=None)
#             file.conversation_path = f'{USER_READ_CONSERVATION_PATH}/{file.user_id.id}_{file.title}.txt'
#             conversation_path = file.conversation_path
#             file.save()
#         else:
#             conversation_path = file.conversation_path
#             with open(conversation_path, 'r') as f:
#                 conversation = json.load(f)
#         conversation.append({'role': 'user', 'content': question})
#         # 从数据库中找到最相似的段落
#
#             # print(f"Received data (Client ID {client_id}): {data}")
#         elif decoded_line.startswith('event'):
#             event_type = decoded_line.replace('event: ', '')
#             # print(f"Event type: {event_type}")
#     finally:
#         response.close()
#     # print(response)  # 目前不清楚是何种返回 TODO:
#     return reply.success({"ai_reply": ai_reply, "docs": origin_docs}, msg="成功")
@require_http_methods(["POST"])
def clear_conversation(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    request_data = json.loads(request.body)
    file_reading_id = request_data.get('file_reading_id')
    fr = FileReading.objects.get(id=file_reading_id)
    with open(fr.conversation_path, 'w') as f:
        json.dump({"conversation": []}, f, indent=4)
    return reply.success(msg="清除对话历史成功")
