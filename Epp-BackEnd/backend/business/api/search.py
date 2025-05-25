
'''
本文件主要处理搜索功能，包括向量化检索和对话检索
API格式如下：
api/serach/...
'''
import re

import Levenshtein
from django.views.decorators.http import require_http_methods
from business.models.problem import problem_record

# def insert_search_record_2_kb(search_record_id, tmp_kb_id):
#     search_record_id = str(search_record_id)
#     with open(settings.USER_SEARCH_MAP_PATH, "r") as f:
#         s_2_kb_map = json.load(f)
#     s_2_kb_map = {str(k): v for k, v in s_2_kb_map.items()}
#     if search_record_id in s_2_kb_map.keys():
#         if delete_tmp_kb(s_2_kb_map[search_record_id]):
#             print("删除TmpKb成功")
#         else:
#             print("删除TmpKb失败")

#     s_2_kb_map[search_record_id] = tmp_kb_id
#     with open(settings.USER_SEARCH_MAP_PATH, "w") as f:
#         json.dump(s_2_kb_map, f, indent=4)


def insert_search_record_2_kb(search_record_id, tmp_kb_id):
    # 调试：打印输入参数
    # print(f"函数 insert_search_record_2_kb 被调用，参数：search_record_id={search_record_id}, tmp_kb_id={tmp_kb_id}")

    # 转换 search_record_id 为字符串
    search_record_id = str(search_record_id)
    # print(f"已将 search_record_id 转换为字符串：{search_record_id}")

    # 调试：检查文件路径是否存在
    # print(f"检查文件路径：{settings.USER_SEARCH_MAP_PATH}")
    if not os.path.exists(settings.USER_SEARCH_MAP_PATH):
        # print(f"文件 {settings.USER_SEARCH_MAP_PATH} 不存在，正在创建新文件。")
        # 创建新文件并写入空的 JSON 对象
        with open(settings.USER_SEARCH_MAP_PATH, "w") as f:
            json.dump({}, f, indent=4)
        # print(f"已成功创建新文件：{settings.USER_SEARCH_MAP_PATH}")

    try:
        # 读取 JSON 文件
        with open(settings.USER_SEARCH_MAP_PATH, "r") as f:
            s_2_kb_map = json.load(f)
        # print(f"从文件加载的 s_2_kb_map：{s_2_kb_map}")

        # 调试：检查映射关系
        # print(f"当前的 s_2_kb_map：{s_2_kb_map}")

        # 转换键为字符串
        s_2_kb_map = {str(k): v for k, v in s_2_kb_map.items()}
        # print(f"已将 s_2_kb_map 的键转换为字符串：{s_2_kb_map}")

        # 检查 search_record_id 是否已存在
        if search_record_id in s_2_kb_map:
            # print(f"发现 search_record_id 已存在：{search_record_id}，当前对应的 tmp_kb_id：{s_2_kb_map[search_record_id]}")

            # 调试：尝试删除旧的 tmp_kb
            old_tmp_kb_id = s_2_kb_map[search_record_id]
            # print(f"尝试删除旧的 tmp_kb_id：{old_tmp_kb_id}")

            if delete_tmp_kb(old_tmp_kb_id):
                print("删除 TmpKb 成功")
            else:
                print("删除 TmpKb 失败")
        else:
            print(f"未找到 search_record_id：{search_record_id} 的现有记录")

        # 更新映射关系
        s_2_kb_map[search_record_id] = tmp_kb_id
        # print(f"已更新 s_2_kb_map：{s_2_kb_map}")

        # 写入 JSON 文件
        with open(settings.USER_SEARCH_MAP_PATH, "w") as f:
            json.dump(s_2_kb_map, f, indent=4)
        # print(f"已成功将更新后的 s_2_kb_map 写入文件：{settings.USER_SEARCH_MAP_PATH}")

    except Exception as e:
        print(f"发生错误：{e}")
        raise  # 如果需要，可以重新抛出异常以便进一步处理

def get_tmp_kb_id(search_record_id):
    with open(settings.USER_SEARCH_MAP_PATH, "r") as f:
        s_2_kb_map = json.load(f)
    # print(f_2_kb_map)
    if str(search_record_id) in s_2_kb_map:
        return s_2_kb_map[str(search_record_id)]
    else:
        return None


def queryGLM(msg: str, history=None) -> str:
    '''
    对chatGLM3-6B发出一次单纯的询问(目前改为zhipu-api)
    '''
    openai.api_base = f'http://{settings.REMOTE_CHATCHAT_GLM3_OPENAI_PATH}/v1'
    openai.api_key = "none"
    if history is None:
        history = [{'role' : 'user', 'content': msg}]
    else:
        history.extend([{'role' : 'user', 'content': msg}])
    response = openai.ChatCompletion.create(
        model="zhipu-api",
        messages=history,
        stream=False
    )
    return response.choices[0].message.content


def search_papers_by_keywords(keywords):
    # 初始化查询条件，此时没有任何条件，查询将返回所有Paper对象
    query = Q()

    # 为每个关键词添加搜索条件
    for keyword in keywords:
        query |= Q(title__icontains=keyword) | Q(abstract__icontains=keyword)

    # 使用累积的查询条件执行查询
    result = Paper.objects.filter(query)
    filtered_paper_list = []
    for paper in result:
        filtered_paper_list.append(paper)
    return filtered_paper_list


# def update_search_record_2_paper(search_record, filtered_papers):
#     search_record.related_papers.clear()
#     for paper in filtered_papers:
#         search_record.related_papers.add(paper)


# @require_http_methods(["POST"])
# def vector_query(request):
#     """
#     本函数用于处理向量化检索的请求，search_record含不存在则创建，存在（需传参数）则恢复两种情况
#     此类检索不包含上下文信息，仅用当前提问对本地知识库检索即可
#     :param Request: 请求，类型为GET
#         内容包含：{
#             "search_content": 检索关键词
#         }
#     :return: 返回一个json对象，其中为一个列表，列表中的每个元素为一个文献的信息
#     {
#         [
#             {
#                 "paper_id": 文献id,
#                 "title": 文献标题,
#                 "authors": 作者,
#                 "abstract": 摘要,
#                 "time": 发布时间,
#                 "journal": 期刊,
#                 "ref_cnt": 引用次数,
#                 "original_url": 原文地址,
#                 "read_count": 阅读次数
#             }
#         ]
#     }
#
#     TODO:
#         1. 从Request中获取user_id和search_content
#         2. 将search_content存入数据库
#         3. 使用向量检索从数据库中获取文献信息
#         4. 返回文献信息
#     """
#     # 鉴权
#     username = request.session.get('username')
#     if username is None:
#         username = 'sanyuba'
#     user = User.objects.filter(username=username).first()
#     if user is None:
#         return reply.fail(msg="请先正确登录")
#
#     request_data = json.loads(request.body)
#     search_content = request_data.get('search_content')
#     ai_reply = ""
#     # filtered_paper = search_paper_with_query(search_content, limit=200) 从这里改为使用服务器的查询接口
#     vector_filtered_papers = get_filtered_paper(search_content, k=100, threshold=0.3)  # 这是新版的调用服务器模型的接口
#
#     # 进行二次关键词检索
#     # 首先获取关键词, 同样使用chatglm6b的普通对话
#     chat_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/chat'
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     payload = json.dumps({
#         "query": search_content,
#         "prompt_name": "keyword",
#         "temperature": 0.3
#     })
#     response = requests.request("POST", chat_chat_url, data=payload, headers=headers, stream=False)
#     keyword = ""
#
#     decoded_line = response.iter_lines().__next__().decode('utf-8')
#     # print(decoded_line)
#     if decoded_line.startswith('data'):
#         data = json.loads(decoded_line.replace('data: ', ''))
#         keyword += data['text']
#
#     print(keyword)
#     keywords = keyword.split(", ")  # ["aa", "bb"]
#     not_keywords = ["paper", "research", "article"]
#     for not_keyword in not_keywords:
#         keywords = [keyword for keyword in keywords if not_keyword not in keyword]
#
#     keyword_filtered_papers = search_papers_by_keywords(keywords=keywords)
#
#     if len(keyword_filtered_papers) > 20:
#         keyword_filtered_papers = keyword_filtered_papers[:20]
#
#     s1 = set(vector_filtered_papers)
#     s2 = set(keyword_filtered_papers)
#     filtered_papers = list(s1.union(s2))
#
#     start_year = min([paper.publication_date.year for paper in filtered_papers])
#     end_year = max([paper.publication_date.year for paper in filtered_papers])
#
#     # 发表数量最多的年份
#     most_year = max(set([paper.publication_date.year for paper in filtered_papers]),
#                     key=[paper.publication_date.year for paper in filtered_papers].count)
#
#     cnt = len([1 for paper in filtered_papers if paper.publication_date.year == most_year])
#     ai_reply += (f'根据您的需求，Epp论文助手检索到了【{len(filtered_papers)}】篇论文，其主要分布在【{start_year}】'
#                  f'到【{end_year}】之间，其中【{most_year}】这一年的论文数量最多，有【{cnt}】篇论文,'
#                  f'显示出近几年在该领域的研究活跃度较高。\n')
#     # return reply.success({"keyword": keyword, 'papers': filtered_paper})
#
#     # return reply.success({"data": "成功", "content": content})
#     # 进行总结， 输入标题/摘要
#     # papers_summary = f"关键词："
#     # papers_summary = "下述论文与主题"
#     # for keyword in keywords:
#     #     papers_summary += keyword + "，"
#     # papers_summary += "密切相关\n"
#     papers_summary = ""
#     for paper in filtered_papers[:20]:
#         papers_summary += f'{paper.title}\n'
#         # papers_summary += f'摘要为：{paper.abstract}\n'
#
#     payload = json.dumps({
#         "query": papers_summary,
#         "prompt_name": "query_summary",
#         "temperature": 0.3
#     })
#
#     response = requests.request("POST", chat_chat_url, data=payload, headers=headers, stream=False)
#     if response.status_code == 200:
#         lines = response.iter_lines()
#         for line in lines:
#             decoded_line = line.decode('utf-8')
#             print(decoded_line)
#             if decoded_line.startswith('data'):
#                 data = json.loads(decoded_line.replace('data: ', ''))
#                 ai_reply += data['text']
#             print(f'ai_reply: {ai_reply}')
#     else:
#         return reply.fail(msg='检索总结失败，请检查网络并重新尝试')
#
#     # 判断是创建检索/恢复检索
#     search_record_id = request_data.get('search_record_id')
#     if search_record_id is None:
#         search_record = SearchRecord(user_id=user, keyword=search_content, conversation_path=None)
#         search_record.save()
#         conversation_path = os.path.join(settings.USER_SEARCH_CONSERVATION_PATH,
#                                          str(search_record.search_record_id) + '.json')
#         if os.path.exists(conversation_path):
#             os.remove(conversation_path)
#         with open(conversation_path, 'w') as f:
#             json.dump({"conversation": []}, f, indent=4)
#         search_record.conversation_path = conversation_path
#         search_record.save()
#     else:
#         search_record = SearchRecord.objects.get(search_record_id=search_record_id)
#         conversation_path = search_record.conversation_path
#
#     update_search_record_2_paper(search_record, filtered_papers)
#
#     # 处理历史记录部分, 无需向前端传递历史记录, 仅需对话文件中添加
#     with open(conversation_path, 'r') as f:
#         conversation_history = json.load(f)
#
#     conversation_history = list(conversation_history.get('conversation'))
#     conversation_history.extend([{
#         "role": "user",
#         "content": search_content
#     }, {
#         "role": "assistant",
#         "content": ai_reply
#     }])
#
#     with open(conversation_path, 'w') as f:
#         json.dump({"conversation": conversation_history}, f, indent=4)
#
#     # 将paper转化为json
#     filtered_papers_list = []
#     for p in filtered_papers:
#         filtered_papers_list.append(p.to_dict())
#
#     ### 构建知识库 ###
#
#     try:
#         tmp_kb_id = build_abs_kb_by_paper_ids([paper.paper_id for paper in filtered_papers], search_record_id)
#         insert_search_record_2_kb(search_record.search_record_id, tmp_kb_id)
#     except Exception as e:
#         return reply.fail(msg="构建知识库失败")
#
#     return JsonResponse({"paper_infos": filtered_papers_list, 'ai_reply': ai_reply, 'keywords': keywords, 'search_record_id' : search_record.search_record_id}, status=200)


@require_http_methods(["GET"])
def restore_search_record(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    search_record_id = request.GET.get('search_record_id')
    search_record = SearchRecord.objects.get(search_record_id=search_record_id)
    conversation_path = search_record.conversation_path
    with open(conversation_path, 'r') as f:
        history = json.load(f)

    # 取出全部对应论文
    paper_infos = []
    papers = search_record.related_papers.all()
    for paper in papers:
        paper_infos.append(paper.to_dict())
    history['paper_infos'] = paper_infos
    try:
        kb_id = build_abs_kb_by_paper_ids([paper.paper_id for paper in papers], search_record.search_record_id)
        insert_search_record_2_kb(search_record_id, kb_id)
        # history['kb_id'] = kb_id
    except Exception as e:
        return reply.fail(msg="构建知识库失败")

    return reply.success(history)


@require_http_methods(["GET"])
def get_user_search_history(request):
    username = request.session.get('username')
    if username is None:
        username = 'Ank'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")
    search_records = SearchRecord.objects.filter(user_id=user).order_by('-date')
    keywords = []
    for item in search_records:
        keywords.append(item.keyword)

    return reply.success({"keywords": list(set(keywords))[:10]})

# def kb_ask_ai(payload):
#     ''''
#     payload = json.dumps({
#         "query": query,
#         "knowledge_id": tmp_kb_id,
#         "history": conversation_history[-10:],
#         "prompt_name": "text"  # 使用历史记录对话模式
#     })
#     payload = json.dumps({
#         "query": query,
#         "knowledge_id": tmp_kb_id,
#         "prompt_name": "default"  # 使用普通对话模式
#     })
#     '''
#     file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     response = requests.request("POST", file_chat_url, data=payload, headers=headers, stream=False)
#     ai_reply = ""
#     origin_docs = []
#     print(response)
#     for line in response.iter_lines():
#         if line:
#             decoded_line = line.decode('utf-8')
#             if decoded_line.startswith('data'):
#                 data = decoded_line.replace('data: ', '')
#                 data = json.loads(data)
#                 ai_reply += data["answer"]
#                 for doc in data["docs"]:
#                     doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
#                     origin_docs.append(doc)
#     return ai_reply, origin_docs

# @require_http_methods(["POST"])
# def dialog_query(request):
#     """
#     本函数用于处理对话检索的请求
#     :param Request: 请求，类型为POST
#         内容包含：{
#             message: string
#             ,
#             paper_ids:[
#                 string, //很多个paper_id
#             ]
#             ,
#             tmp_kb_id : string // 临时知识库id
#         }
        
#     :return: 返回一个json对象，格式为：
#     {
#         dialog_type: 'dialog' or 'query',
#         papers:[
#             {//只有在dialog_type为'query'时才有，这时需要前端对文献卡片进行渲染。
#                 "paper_id": 文献id,
#                 "title": 文献标题,
#                 "authors": 作者,
#                 "abstract": 摘要,
#                 "publication_date": 发布时间,
#                 "journal": 期刊,
#                 "citation_count": 引用次数,
#                 "original_url": 原文地址,
#                 "read_count": 阅读次数
#             },
#         ],
#         content: '回复内容'
#     }
    
    # TODO:
    #     1. 从Request中获取对话内容
    #     2. 根据最后一条user的对话回答进行关键词触发，分析属于哪种对话类型
    #         - 如果对话类型为'query'
    #             1. 使用向量检索从数据库中获取文献信息 5篇
    #             2. 将文献信息整理为json，作为papers属性
    #             3. 将文献信息进行整理作为content属性
    #         - 如果对话类型为'dialog'
    #             1. 大模型正常推理就可以了
    #     3. 把聊天记录存在本地
    #     4. 返回json对象,存入到数据库，见backend/business/models/search_record.py
    # """
    # import os
    # username = request.session.get('username')
    # if username is None:
    #     username = 'sanyuba'
    # data = json.loads(request.body)
    # message = data.get('message')
    # search_record_id = data.get('search_record_id')

    # problem_obj, created = problem_record.objects.get_or_create(content=message)
    # problem_obj.number = problem_obj.number + 1 if not created else 1  # 简洁写法
    # problem_obj.save()

#     kb_id = get_tmp_kb_id(search_record_id)
#     # kb_id = 0

#     user = User.objects.filter(username=username).first()
#     if user is None:
#         return JsonResponse({'error': '用户不存在'}, status=404)
#     search_record = SearchRecord.objects.filter(search_record_id=search_record_id).first()
#     conversation_path = settings.USER_SEARCH_CONSERVATION_PATH + '/' + str(search_record.search_record_id) + '.json'
#     history = []
#     if os.path.exists(conversation_path):
#         c = json.loads(open(conversation_path).read())
#         history = c
#     # 先判断下是不是要查询论文
#     prompt = '想象你是一个科研助手，你手上有一些论文，你判断用户的需求是不是要求你去检索新的论文，你的回答只能是\"yes\"或者\"no\"，他的需求是：\n' + message + '\n'
#     response_type = queryGLM(prompt)
#     papers = []
#     dialog_type = ''
#     content = ''
#     print(response_type)
#     if 'yes' in response_type:  # 担心可能有句号等等
#         # 查询论文，TODO:接入向量化检索
#         # filtered_paper = query_with_vector(message) # 旧版的接口，换掉了 2024.4.28
#         filtered_paper = get_filtered_paper(text=message, k=5)
#         dialog_type = 'query'
#         papers = []
#         for paper in filtered_paper:
#             papers.append(paper.to_dict())
#         print(papers)
#         content = '根据您的需求，我们检索到了一些论文信息'
#         # for i in range(len(papers)):
#         #     content + '\n' + f'第{i}篇：'
#         #     # TODO: 这里需要把papers的信息整理到content里面
#         #     content += f'标题为：{papers[i]["title"]}\n'
#         #     content += f'摘要为：{papers[i]["abstract"]}\n'
#     else:

#         ############################################################

#         ## 这部分重新重构了，按照方法是通过将左侧的文章重构成为一个知识库进行检索

#         ###########################################################
#         # 对话，保存3轮最多了，担心吃不下

#         input_history = history['conversation'].copy()[-5:] if len(history['conversation']) > 5 else history['conversation'].copy()
#         print(input_history)
#         print('kb_id:', kb_id)
#         print('message:', message)
#         payload = json.dumps({
#             "query": message,
#             "knowledge_id": kb_id,
#             "history": list(input_history),
#             "prompt_name": "text"  # 使用历史记录对话模式
#         })
#         ai_reply, origin_docs = kb_ask_ai(payload)
#         print(ai_reply)
#         dialog_type = 'dialog'
#         papers = []
#         content = queryGLM('你叫epp论文助手，以你的视角重新转述这段话：'+ai_reply, [])
#         history['conversation'].extend([{'role': 'user', 'content': message}])
#         history['conversation'].extend([{'role': 'assistant', 'content': content}])
#     with open(conversation_path, 'w', encoding='utf-8') as f:
#         f.write(json.dumps(history))
#     res = {
#         'dialog_type': dialog_type,
#         'papers': papers,
#         'content': content
#     }
#     return reply.success(res, msg='成功返回对话')


# @require_http_methods(["POST"])
# def build_kb(request):
#     ''''
#     这个方法是论文循证
#     输入为paper_id_list，重新构建一个知识库
#     '''
#     data = json.loads(request.body)
#     paper_id_list = data.get('paper_id_list')
#     try:
#         tmp_kb_id = build_abs_kb_by_paper_ids(paper_id_list, 'tmp_kb')
#     except Exception as e:
#         print(e)
#         return reply.fail(msg="构建知识库失败")
#     return reply.success({'kb_id': tmp_kb_id})

def change_record_papers(request):
    '''
    本函数用于修改搜索记录的论文
    '''
    username = request.session.get('username')
    data = json.loads(request.body)
    search_record_id = data.get('search_record_id')
    paper_id_list = data.get('paper_id_list')
    search_record = SearchRecord.objects.get(search_record_id=search_record_id)
    papers = []
    for paper_id in paper_id_list:
        paper = Paper.objects.get(paper_id=paper_id)
        papers.append(paper)
    search_record.related_papers.clear()
    for paper in papers:
        search_record.related_papers.add(paper)
        
    ### 修改知识库
    try: 
        kb_id = build_abs_kb_by_paper_ids(paper_id_list, search_record_id)
        insert_search_record_2_kb(search_record_id, kb_id)
    except Exception as e:
        return reply.fail(msg="构建知识库失败")
    
    return JsonResponse({'msg': '修改成功'}, status=200)

@require_http_methods(["DELETE"])
def flush(request):
    '''
    这是用来清空对话记录的函数
    :param request: 请求，类型为DEL
        内容包含：{
            search_record_id : string
        }
    '''
    username = request.session.get('username')
    data = json.loads(request.body)
    sr = SearchRecord.objects.get(search_record_id=data.get('search_record_id'))
    if sr is None:
        return JsonResponse({'error': '搜索记录不存在'}, status=404)
    else:
        conversation_path = sr.conversation_path
        import os
        if os.path.exists(conversation_path):
            os.remove(conversation_path)
        sr.delete()
        HttpRequest('清空成功', status=200)

'''
本文件主要处理搜索功能，包括向量化检索和对话检索
API格式如下：
api/serach/...
'''
import json, openai
import os

from django.db.models import Q
from django.http import JsonResponse, HttpRequest
from business.models.search_record import SearchRecord, User
from django.conf import settings

import requests
from business.utils import reply
from business.utils.knowledge_base import delete_tmp_kb, build_abs_kb_by_paper_ids
from business.utils.paper_vdb_init import get_filtered_paper, local_vdb_init


# def insert_search_record_2_kb(search_record_id, tmp_kb_id):
#     search_record_id = str(search_record_id)
#     with open(settings.USER_SEARCH_MAP_PATH, "r") as f:
#         s_2_kb_map = json.load(f)
#     s_2_kb_map = {str(k): v for k, v in s_2_kb_map.items()}
#     if search_record_id in s_2_kb_map.keys():
#         if delete_tmp_kb(s_2_kb_map[search_record_id]):
#             print("删除TmpKb成功")
#         else:
#             print("删除TmpKb失败")

#     s_2_kb_map[search_record_id] = tmp_kb_id
#     with open(settings.USER_SEARCH_MAP_PATH, "w") as f:
#         json.dump(s_2_kb_map, f, indent=4)


def get_tmp_kb_id(search_record_id):
    with open(settings.USER_SEARCH_MAP_PATH, "r") as f:
        s_2_kb_map = json.load(f)
    # print(f_2_kb_map)
    if str(search_record_id) in s_2_kb_map:
        return s_2_kb_map[str(search_record_id)]
    else:
        return None

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# def queryGLM(msg: str, history=None) -> str:
#     '''
#     对chatGLM3-6B发出一次单纯的询问
#     '''
#     print(msg)
#     chat_chat_url = 'http://115.190.109.233:7861/chat/chat'
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     payload = json.dumps({
#         "query": msg,
#         "prompt_name": "default",
#         "temperature": 0.3
#     })

#     session = requests.Session()
#     retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)

#     try:
#         response = session.post(chat_chat_url, data=payload, headers=headers, stream=False)
#         response.raise_for_status()

#         # 确保正确处理分块响应
#         decoded_line = next(response.iter_lines()).decode('utf-8')
#         print("AI回答: ", decoded_line)
#         if decoded_line.startswith('data'):
#             data = json.loads(decoded_line.replace('data: ', ''))
#         else:
#             data = decoded_line
#         return data['text']
#     except requests.exceptions.ChunkedEncodingError as e:
#         print(f"ChunkedEncodingError: {e}")
#         return "错误: 响应提前结束"
#     except requests.exceptions.RequestException as e:
#         print(f"RequestException: {e}")
#         return f"错误: {e}"


from django.views.decorators.http import require_http_methods
from business.models.paper import Paper


def search_papers_by_keywords(keywords):
    # 初始化查询条件，此时没有任何条件，查询将返回所有Paper对象
    query = Q()

    # 为每个关键词添加搜索条件
    for keyword in keywords:
        query |= Q(title__icontains=keyword) | Q(abstract__icontains=keyword)

    # 使用累积的查询条件执行查询
    result = Paper.objects.filter(query)
    filtered_paper_list = []
    for paper in result:
        filtered_paper_list.append(paper)
    return filtered_paper_list


def update_search_record_2_paper(search_record, filtered_papers):
    search_record.related_papers.clear()
    for paper in filtered_papers:
        search_record.related_papers.add(paper)

def do_dialogue_search(search_content, chat_chat_url, headers):
    # filtered_paper = search_paper_with_query(search_content, limit=200) 从这里改为使用服务器的查询接口
    vector_filtered_papers = get_filtered_paper(search_content, k=100, threshold=0.3)  # 这是新版的调用服务器模型的接口

    # 进行二次关键词检索
    # 首先获取关键词, 同样使用chatglm6b的普通对话
    payload = json.dumps({
        "query": search_content,
        "prompt_name": "keyword",
        "temperature": 0.3
    })
    response = requests.request("POST", chat_chat_url, data=payload, headers=headers, stream=False)
    keyword = ""

    decoded_line = response.iter_lines().__next__().decode('utf-8')
    # print(decoded_line)
    if decoded_line.startswith('data'):
        data = json.loads(decoded_line.replace('data: ', ''))
        keyword += data['text']

    print(keyword)
    keywords = keyword.split(", ")  # ["aa", "bb"]
    not_keywords = ["paper", "research", "article"]
    for not_keyword in not_keywords:
        keywords = [keyword for keyword in keywords if not_keyword not in keyword]

    keyword_filtered_papers = search_papers_by_keywords(keywords=keywords)

    if len(keyword_filtered_papers) > 20:
        keyword_filtered_papers = keyword_filtered_papers[:20]

    s1 = set(vector_filtered_papers)
    s2 = set(keyword_filtered_papers)
    filtered_papers = list(s1.union(s2))
    return filtered_papers

def search_my_model(query_string):
    # 将字符串按空格切割
    search_terms = query_string.split()

    # 构造一个 Q 对象，用于模糊查询
    query = Q()
    for term in search_terms:
        query |= Q(x__icontains=term)

    # 执行查询，获取并集结果
    results = Paper.objects.filter(query)

    return results

def do_string_search(search_content, max_results=20):
    pattern = r'[,\s!?.]+'
    search_terms = re.split(pattern, search_content)
    search_terms = [token for token in search_terms if token]
    print(search_terms)
    query = Q()
    for term in search_terms:
        query |= Q(title__icontains=term)

    print(query)
    # 执行查询，获取字符串检索的并集结果
    results = Paper.objects.filter(query)
    print(results)
    # 计算编辑距离并排序
    results_with_distance = []
    for result in results:
        distance = Levenshtein.distance(result.title, search_content)
        print(distance)
        results_with_distance.append((distance, result))
    print(results_with_distance)
    # 按编辑距离排序
    results_with_distance.sort(key=lambda x: x[0])

    # 返回排序后的结果
    sorted_results = [result for distance, result in results_with_distance]
    print("--------------------------------------------------")
    print(sorted_results[:max_results])
    return sorted_results[:max_results]  # 返回前10篇相似度最高的文章

def do_similar_string_search(search_content, max_results=10):
    pattern = r'[,\s!?.]+'
    search_terms = re.split(pattern, search_content)
    search_terms = [token for token in search_terms if token]
    print(search_terms)
    query = Q()
    for term in search_terms:
        query |= Q(title__icontains=term)

    print(query)
    # 执行查询，获取字符串检索的并集结果
    results = Paper.objects.filter(query)
    # print(results)
    # 计算编辑距离并排序
    results_with_distance = []
    for result in results:
        distance = Levenshtein.distance(result.title, search_content)
        results_with_distance.append((distance, result))

    # 按编辑距离排序
    results_with_distance.sort(key=lambda x: x[0])

    # 返回排序后的结果
    sorted_results = [result for distance, result in results_with_distance]
    return sorted_results[:max_results]  # 返回前10篇相似度最高的文章

def search_papers(keywords, start_year=None, end_year=None, authors=None, max_results=10):
    print("search_papers参数设置: keywords: ", keywords, "start_year: ", start_year, "end_year: ", end_year, "authors: ", authors, "max_results: ", max_results)
    query = Q()

    # 关键词搜索（标题/摘要）
    if keywords:
        keyword_query = Q()
        for keyword in keywords:
            keyword_query |= Q(title__icontains=keyword) | Q(abstract__icontains=keyword)
        query &= keyword_query

    # 作者搜索（处理逗号分隔的字符串）
    if authors:
        author_query = Q()
        for author in authors:
            # 增加前后逗号的精确匹配（防止匹配到名字片段）
            author_query |= Q(authors__icontains=author)
            # 更精确的方式（需处理首尾作者的情况）：
            # author_query |= Q(authors__startswith=f"{author},") | 
            #                 Q(authors__contains=f",{author},") |
            #                 Q(authors__endswith=f",{author}")
        query &= author_query

    # 时间范围过滤（处理DateField的年份）
    if start_year is not None:
        query &= Q(publication_date__year__gte=start_year)
    if end_year is not None:
        query &= Q(publication_date__year__lte=end_year)

    # 执行查询（添加时间倒序排序）
    results = Paper.objects.filter(query).order_by('-publication_date')
    
    # 去重处理（虽然主键唯一，但可能因多对多关系产生重复）
    if authors or keywords:
        results = results.distinct()
    
    print("search_papers返回结果: ")
    for result in results[:max_results]:
        print(result.title + " " + str(result.publication_date) + " " + result.authors)
    return list(results[:max_results])

def extract_search_conditions(query: str):


    """
    使用AI提取结构化搜索条件
    
    参数：
    query: 用户自然语言查询
    
    返回：json格式查找条件
    """
    prompt = f"""您是一个专业的学术搜索引擎解析器，请从查询{query}中提取信息，返回格式如下：

  "keywords": [],  # 研究主题相关词汇
  "start_year": 2010,  # 开始年份（含）
  "end_year":  2022    # 结束年份（含）
  "authors": [],  # 作者名称


解析规则：
1. 时间相关表述处理：
   - "XX年以前" -> end_year=XX-1
   - "XX年之后" -> start_year=XX+1，end_year=2025
   - "XX到YY年间" -> start_year=XX, end_year=YY
   - "最近N年" -> start_year=2025-N，end_year=2025

2. 逻辑关系处理：
   - "包含A和B" -> 逻辑AND
   - "A或B" -> 逻辑OR
   - "排除C" -> NOT条件

3. 特殊语义转换：
   - "最新研究" -> start_year=2023，end_year=2025

4.如果相关词汇与作者名称没有提取到对应属性，则保持这两项对应的列表为空

5.start_year默认为2010， end_year默认为2022

6.研究主题相关词汇用英文输出

返回纯JSON对象，不要额外解释"""

    try:
        r = queryGLM(prompt)
        result = json.loads(r)
        print(result)
        return result
    except Exception as e:
        print(f"提取出错: {e}")

    # 如果提取失败，返回None,后边根据None
    return None

@require_http_methods(["POST"])
def vector_query(request):
    """
    本函数用于处理向量化检索的请求，search_record含不存在则创建，存在（需传参数）则恢复两种情况
    此类检索不包含上下文信息，仅用当前提问对本地知识库检索即可
    :param Request: 请求，类型为GET
        内容包含：{
            "search_content": 检索关键词
        }
    :return: 返回一个json对象，其中为一个列表，列表中的每个元素为一个文献的信息
    {
        [
            {
                "paper_id": 文献id,
                "title": 文献标题,
                "authors": 作者,
                "abstract": 摘要,
                "time": 发布时间,
                "journal": 期刊,
                "ref_cnt": 引用次数,
                "original_url": 原文地址,
                "read_count": 阅读次数
            }
        ]
    }

    TODO:
        1. 从Request中获取user_id和search_content
        2. 将search_content存入数据库
        3. 使用向量检索从数据库中获取文献信息
        4. 返回文献信息
    """
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    request_data = json.loads(request.body)
    search_content = request_data.get('search_content')
    search_type = request_data.get('search_type')
    search_record_id = request_data.get('search_record_id')
    if search_record_id is None:
        search_record = SearchRecord(user_id=user, keyword=search_content, conversation_path=None)
        search_record.save()
        print("成功保存搜索记录")
        conversation_path = os.path.join(settings.USER_SEARCH_CONSERVATION_PATH,
                                         str(search_record.search_record_id) + '.json')
        if os.path.exists(conversation_path):
            os.remove(conversation_path)
        with open(conversation_path, 'w') as f:
            json.dump({"conversation": []}, f, indent=4)
        search_record.conversation_path = conversation_path
        search_record.save()
        search_record_id = search_record.search_record_id
    else:
        search_record = SearchRecord.objects.get(search_record_id=search_record_id)
        conversation_path = search_record.conversation_path

    chat_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/chat'
    headers = {
        'Content-Type': 'application/json'
    }

    print("search_type: ", search_type)
    
    # local_vdb_init(None)

    if search_type == 'dialogue':
        filtered_papers = do_dialogue_search(search_content, chat_chat_url, headers)
    else:
        # filtered_papers = do_string_search(search_content)
        filtered_papers = get_filtered_paper(search_content, 20)
        if len(filtered_papers) == 0:
            return JsonResponse({"paper_infos": [], 'ai_reply': "EPP助手哭哭惹，很遗憾未能检索出相关论文。",
                                 'search_record_id': search_record.search_record_id}, status=200)

    start_year = min([paper.publication_date.year for paper in filtered_papers])
    end_year = max([paper.publication_date.year for paper in filtered_papers])

    # 发表数量最多的年份
    most_year = max(set([paper.publication_date.year for paper in filtered_papers]),
                    key=[paper.publication_date.year for paper in filtered_papers].count)

    cnt = len([1 for paper in filtered_papers if paper.publication_date.year == most_year])

    ai_reply = (f'根据您的需求，Epp论文助手检索到了【{len(filtered_papers)}】篇论文，其主要分布在【{start_year}】'
                 f'到【{end_year}】之间，其中【{most_year}】这一年的论文数量最多，有【{cnt}】篇论文,'
                 f'显示出近几年在该领域的研究活跃度较高。\n')
    # return reply.success({"keyword": keyword, 'papers': filtered_paper})

    # return reply.success({"data": "成功", "content": content})
    # 进行总结， 输入标题/摘要
    # papers_summary = f"关键词："
    # papers_summary = "下述论文与主题"
    # for keyword in keywords:
    #     papers_summary += keyword + "，"
    # papers_summary += "密切相关\n"
    papers_summary = ""
    for paper in filtered_papers[:20]:
        papers_summary += f'{paper.title}\n'
        # papers_summary += f'摘要为：{paper.abstract}\n'

    payload = json.dumps({
        "query": papers_summary,
        "prompt_name": "query_summary",
        "temperature": 0.3
    })

    # response = requests.request("POST", chat_chat_url, data=payload, headers=headers, stream=False)
    # if response.status_code == 200:
    #     lines = response.iter_lines()
    #     for line in lines:
    #         decoded_line = line.decode('utf-8')
    #         print(decoded_line)
    #         if decoded_line.startswith('data'):
    #             data = json.loads(decoded_line.replace('data: ', ''))
    #             ai_reply += data['text']
    #         print(f'ai_reply: {ai_reply}')
    # else:
    #     return reply.fail(msg='检索总结失败，请检查网络并重新尝试')

    print("搜索记录id: ", search_record.search_record_id)
    update_search_record_2_paper(search_record, filtered_papers)

    # 处理历史记录部分, 无需向前端传递历史记录, 仅需对话文件中添加
    with open(conversation_path, 'r') as f:
        conversation_history = json.load(f)

    conversation_history = list(conversation_history.get('conversation'))
    conversation_history.extend([{
        "role": "user",
        "content": search_content
    }, {
        "role": "assistant",
        "content": ai_reply
    }])

    with open(conversation_path, 'w') as f:
        json.dump({"conversation": conversation_history}, f, indent=4)

    # 将paper转化为json
    filtered_papers_list = []
    for p in filtered_papers:
        filtered_papers_list.append(p.to_dict())
    
    ### TODO 构建知识库 ###
    
    # try:
    #     tmp_kb_id = build_abs_kb_by_paper_ids([paper.paper_id for paper in filtered_papers], search_record_id)
    #     insert_search_record_2_kb(search_record.search_record_id, tmp_kb_id)
    # except Exception as e:
    #     print("构建知识库失败")
    #     return reply.fail(msg="构建知识库失败")

    print("向量检索完成")
    # 'keywords': keywords
    return JsonResponse({"paper_infos": filtered_papers_list, 'ai_reply': ai_reply, 'search_record_id' : search_record.search_record_id}, status=200)


@require_http_methods('POST')
def vector_query_build_kb(request):
    '''
        {
            'paperIDs',
            'searchRecordID'
        }
    '''
    data = json.loads(request.body)
    paper_id_list = data['paperIDs']
    search_record_id = data['searchRecordId']

    try:
        tmp_kb_id = build_abs_kb_by_paper_ids(paper_id_list, search_record_id)
        insert_search_record_2_kb(search_record_id, tmp_kb_id)
    except Exception as e:
        print("构建知识库失败")
        return reply.fail(msg="构建知识库失败")

    return reply.success(msg="成功构建知识库")



@require_http_methods(["GET"])
def restore_search_record(request):
    # 鉴权
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")

    search_record_id = request.GET.get('search_record_id')
    search_record = SearchRecord.objects.get(search_record_id=search_record_id)
    conversation_path = search_record.conversation_path
    with open(conversation_path, 'r') as f:
        history = json.load(f)

    # 取出全部对应论文
    paper_infos = []
    papers = search_record.related_papers.all()
    for paper in papers:
        paper_infos.append(paper.to_dict())
    history['paper_infos'] = paper_infos
    try:
        kb_id  = build_abs_kb_by_paper_ids([paper.paper_id for paper in papers], search_record.search_record_id)
        insert_search_record_2_kb(search_record_id, kb_id)
        # history['kb_id'] = kb_id
    except Exception as e:
        return reply.fail(msg="构建知识库失败")

    return reply.success(history)


@require_http_methods(["GET"])
def get_user_search_history(request):
    username = request.session.get('username')
    if username is None:
        username = 'Ank'
    user = User.objects.filter(username=username).first()
    if user is None:
        return reply.fail(msg="请先正确登录")
    search_records = SearchRecord.objects.filter(user_id=user).order_by('-date')
    keywords = []
    for item in search_records:
        keywords.append(item.keyword)

    return reply.success({"keywords": list(set(keywords))[:10]})

def kb_ask_ai(conversation_history, query, tmp_kb_id):
    ''''
    payload = json.dumps({
        "query": query,
        "knowledge_id": tmp_kb_id,
        "history": conversation_history[-10:],
        "prompt_name": "text"  # 使用历史记录对话模式
    })
    payload = json.dumps({
        "query": query,
        "knowledge_id": tmp_kb_id,
        "prompt_name": "default"  # 使用普通对话模式
    })
    '''

    payload = json.dumps({
        "query": query,
        "knowledge_id": tmp_kb_id,
        "history": conversation_history[-10:],
        "prompt_name": "text"  # 使用历史记录对话模式
    })

    file_chat_url = f'http://{settings.REMOTE_MODEL_BASE_PATH}/chat/file_chat'
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", file_chat_url, data=payload, headers=headers, stream=False)
    ai_reply = ""
    origin_docs = []
    print(response)
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data'):
                data = decoded_line.replace('data: ', '')
                data = json.loads(data)
                ai_reply += data["answer"]
                for doc in data["docs"]:
                    doc = str(doc).replace("\n", " ").replace("<span style='color:red'>", "").replace("</span>", "")
                    origin_docs.append(doc)
    return ai_reply, origin_docs

def self_check(query, reply):
    # 2. 自反馈机制
    # 2.1 检查回答质量
    # 2.2 TODO 可以持久化检测报告，返回给多智能体，从而实现自反馈
    ai_reply = reply
    quality_check_prompt = f"""
       请评估以下回答的质量，指出存在的问题：
       问题：{query}
       回答：{ai_reply}

       评估标准：
       1. 准确性 - 信息是否准确无误
       2. 完整性 - 是否全面回答了问题
       3. 清晰度 - 表达是否清晰易懂
       4. 相关性 - 内容是否紧密围绕问题

       请按以下格式返回评估结果：
       {{
           "accuracy": 评分(1-5),
           "completeness": 评分(1-5),
           "clarity": 评分(1-5),
           "relevance": 评分(1-5),
           "issues": ["具体问题描述1", "具体问题描述2"]
       }}
       """

    quality_report = queryGLM(quality_check_prompt)
    print("质量评估报告:", quality_report)

    try:
        quality_data = json.loads(quality_report)
        # 如果任何一项评分低于3分，则进行修正
        if any(score < 3 for score in [quality_data["accuracy"], quality_data["completeness"],
                                       quality_data["clarity"], quality_data["relevance"]]):
            print("检测到低质量回答，正在进行修正...")
            correction_prompt = f"""
               原始问题：{query}
               初始回答：{ai_reply}
               检测到的问题：{quality_data["issues"]}

               请根据以下要求改进回答：
               1. 修正不准确的信息
               2. 补充缺失的重要内容
               3. 使表达更加清晰专业
               4. 保持回答简洁明了
               5. 保持专业学术风格
               6. 修正语法和表达错误
               7. 优化段落结构
               8. 保持原意的完整性
               返回改进后的回答：
               """
            ai_reply = queryGLM(correction_prompt)
            print("修正后的回答:", ai_reply)
            return ai_reply
    except:
        print("质量评估解析失败，使用原始回答")
        return reply


def get_final_answer(conversation_history, query, tmp_kb_id):
    from scripts.routing_agent import generate_subtasks,get_expert_weights
    q_type, subtasks = generate_subtasks(query)
    print("多智能体：完成子问题生成")
    print(q_type, subtasks)

    print("多智能体：开始问题分发")
    if q_type == "other":
        print("other type")
        # llm
        return kb_ask_ai(conversation_history, query, tmp_kb_id)
    else:
        api_reply, docs_from_api,search_reply, docs_from_search,llm_reply, origin_docs = three_api_answer(conversation_history, tmp_kb_id, subtasks)

    # 整合
    from scripts.generate_result import aggregate_answers
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

    ai_reply = self_check(query, ai_reply)

    return ai_reply, docs

def get_api_reply(api_query):#获取本地RAG以及google scholar api检索文献结果（google scholar api有使用限制，还是以本地RAG为主）
    from scripts.test_classifyAndGenerate1 import test_localvdb_and_scholarapi #先从scripts里import，之后要把这个文件中的方法移到utils里
    return test_localvdb_and_scholarapi(api_query)


def get_search_reply(search_query): #获取tavily搜索引擎专家的结果
    from scripts.tavily_test import tavily_advanced_search #先从scripts里import，之后要把tavily这个文件移到utils里
    search_list = tavily_advanced_search(search_query).get("results")
    # print(search_list)

    from business.utils.text_summarizer import text_summarizer

    search_reply = ""
    docs = []
    for r in search_list:
        title = r['title']
        search_reply += f"- [{title}] "

        content = r['raw_content'] if r['raw_content'] else r['content']
        cnt = 10
        while len(content) > 2000 and cnt > 0:
            content = text_summarizer(content, cnt)
            cnt -= 1
        search_reply += f"{content}\n"

        search_reply += f"score: {r['score']}\n\n"

        docs.append(r['title'] + "   "+ r['url'])

    summarized_search_reply = text_summarizer(search_reply, 10)

    return summarized_search_reply, docs


def get_search_reply2(search_query): #获取tavily搜索引擎专家的结果
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
    
    from business.utils.text_summarizer import text_summarizer #对搜索引擎专家产生的结果进行总结
    summarized_search_reply = text_summarizer(search_reply)

    docs = []
    for qa in uselist:
        docs.append(qa['title'] + "   "+ qa['url'])
    #返回示例  ['VQ-VAE Explained - Papers With Code   https://paperswithcode.com/method/vq-vae', 
    # 'PDF   https://xnought.github.io/files/vq_vae_explainer.pdf']

    return summarized_search_reply, docs


import concurrent.futures
import time
def three_api_answer(conversation_history, tmp_kb_id, subtasks):
    # 使用多线程执行三个任务
    start_time = time.time()  # 记录开始时间
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # 提交API任务
        api_future = executor.submit(get_api_reply, subtasks.get("api"))
        
        # 提交搜索任务
        search_future = executor.submit(get_search_reply, subtasks.get("search"))
        
        # 提交LLM任务
        print()
        llm_future = executor.submit(kb_ask_ai, 
                                     conversation_history, 
                                     subtasks.get("llm"), 
                                     tmp_kb_id)
        
        # 获取API结果
        api_reply, docs_from_api = api_future.result()
        
        # 获取搜索结果
        search_reply, docs_from_search = search_future.result()
        
        # 获取LLM结果
        llm_reply, origin_docs = llm_future.result()
    
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

    return api_reply, docs_from_api,search_reply, docs_from_search,llm_reply, origin_docs

@require_http_methods(["POST"])
def dialog_query(request):
    """
    本函数用于处理对话检索的请求
    :param Request: 请求，类型为POST
        内容包含：{
            message: string
            ,
            paper_ids:[
                string, //很多个paper_id
            ]
            ,
            tmp_kb_id : string // 临时知识库id
        }
        
    :return: 返回一个json对象，格式为：
    {
        dialog_type: 'dialog' or 'query',
        papers:[
            {//只有在dialog_type为'query'时才有，这时需要前端对文献卡片进行渲染。
                "paper_id": 文献id,
                "title": 文献标题,
                "authors": 作者,
                "abstract": 摘要,
                "publication_date": 发布时间,
                "journal": 期刊,
                "citation_count": 引用次数,
                "original_url": 原文地址,
                "read_count": 阅读次数
            },
        ],
        content: '回复内容'
    }
    
        1. 从Request中获取对话内容
        2. 根据最后一条user的对话回答进行关键词触发，分析属于哪种对话类型
            - 如果对话类型为'query'
                1. 使用向量检索从数据库中获取文献信息 5篇
                2. 将文献信息整理为json，作为papers属性
                3. 将文献信息进行整理作为content属性
            - 如果对话类型为'dialog'
                1. 大模型正常推理就可以了
        3. 把聊天记录存在本地
        4. 返回json对象,存入到数据库，见backend/business/models/search_record.py
    """
    import os
    username = request.session.get('username')
    if username is None:
        username = 'sanyuba'
    data = json.loads(request.body)
    message = data.get('message')
    search_record_id = data.get('search_record_id')
    # 获取临时知识库id
    kb_id = get_tmp_kb_id(search_record_id) 
    
    user = User.objects.filter(username=username).first()
    if user is None:
        return JsonResponse({'error': '用户不存在'}, status=404)
    search_record = SearchRecord.objects.filter(search_record_id=search_record_id).first()
    conversation_path = settings.USER_SEARCH_CONSERVATION_PATH + '/' + str(search_record.search_record_id) + '.json'
    history = []
    if os.path.exists(conversation_path):
        c = json.loads(open(conversation_path).read())
        history = c
    # 先判断下是不是要查询论文
    # prompt = f"想象你是一个科研助手，你手上有一些论文，你判断用户的需求是不是要求你去检索新的论文，你的回答只能是\"yes\"或者\"no\"，他的需求是：\n' + {message} + '\n"
    prompt = f"""
    你将收到一个查询请求，请判断这个请求是否要求检索相关论文。只有出现“检索”“查找”等关键字时才认为这是一个检索请求。
    如果是，请返回 "yes+关键词"，其中关键词是查询中提到的与论文相关的主题或关键词。例如"yes+Deeplearning"，不要返回多余的信息。
    如果不是，请返回 "no"。

    查询请求：{message}
    """
    response_type = queryGLM(prompt)
    print("是否为检索: ", response_type)
    papers = []
    dialog_type = ''
    content = ''
    # print(response_type)
    if 'yes' in response_type:  # 担心可能有句号等等
        # 查询论文
        # filtered_paper = query_with_vector(message) # 旧版的接口，换掉了 2024.4.28
        search_content = response_type.split('+')[-1].strip()
        print("search_content:", search_content)

        conditions = extract_search_conditions(message)
        
        # filtered_paper = do_string_search(search_content=search_content, max_results=5)   # 字符串匹配，检索效果较差
        # 若以下方法报错，请先运行business\utils\paper_vdb_init.py中的local_vdb_init方法对本地向量库进行初始化,初始化之后注掉这个方法即可
        # local_vdb_init(None)
        filtered_paper=[]
        if conditions == None:
            filtered_paper = get_filtered_paper(text=message, k=5)
        else:
            filtered_paper = search_papers(keywords=conditions["keywords"], start_year=conditions["start_year"], end_year=conditions["end_year"],authors=conditions["authors"])
        print("filtered_paper: ", filtered_paper)
        dialog_type = 'query'
        papers = []
        for paper in filtered_paper:
            papers.append(paper.to_dict())
        # print(papers)
        content = '根据您的需求，我们检索到了一些论文信息'
        if len(filtered_paper) == 0:
            dialog_type = 'dialog'
            content = "抱歉，没有查找到相关论文"
        for i in range(len(papers)):
            content += '\n' + f'第{i+1}篇：' + papers[i]['title']
            # content += '\n' + f'第{i+1}篇：'
            # content += f'标题为：{papers[i]["title"]}\n'
            # content += f'摘要为：{papers[i]["abstract"]}\n'
        content += '\n'
    else:

        ############################################################

        ## 这部分重新重构了，按照方法是通过将左侧的文章重构成为一个知识库进行检索

        ###########################################################
        # 对话，保存3轮最多了，担心吃不下

        input_history = history['conversation'].copy()[-5:] if len(history['conversation']) > 5 else history['conversation'].copy()
        # print("对话历史", input_history)
        print('kb_id:', kb_id)
        print('message:', message)
        # payload = json.dumps({
        #     "query": message,
        #     "knowledge_id": kb_id,
        #     "history": list(input_history),
        #     "prompt_name": "text"  # 使用历史记录对话模式
        # })
        # ai_reply, origin_docs = kb_ask_ai(payload)
        # ai_reply = queryGLM(message, input_history)
        # print("ai_reply: ", ai_reply)
        ai_reply, origin_docs = get_final_answer(input_history, message, kb_id)
        dialog_type = 'dialog'
        papers = []
        content = queryGLM('你叫epp论文助手，以你的视角重新转述这段话（注意不要出现作为EPP论文助手等语句，直接给出转述后的内容）：' + ai_reply, [])
        history['conversation'].extend([{'role': 'user', 'content': message}])
        history['conversation'].extend([{'role': 'assistant', 'content': content}])
    with open(conversation_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(history))

    from business.utils.ai.get_explainationwords import get_keywords
    words = get_keywords(content)

    res = {
        'dialog_type': dialog_type,
        'papers': papers,
        'content': content,
        'highlights': words
    }
    return reply.success(res, msg='成功返回对话')


@require_http_methods(["POST"])
def build_kb(request):
    ''''
    这个方法是论文循证
    输入为paper_id_list，重新构建一个知识库
    '''
    data = json.loads(request.body)
    paper_id_list = data.get('paper_id_list')
    try:
        tmp_kb_id = build_abs_kb_by_paper_ids(paper_id_list, 'tmp_kb')
    except Exception as e:
        print(e)
        return reply.fail(msg="构建知识库失败")
    return reply.success({'kb_id': tmp_kb_id})

def change_record_papers(request):
    '''
    本函数用于修改搜索记录的论文
    '''
    username = request.session.get('username')
    data = json.loads(request.body)
    search_record_id = data.get('search_record_id')
    paper_id_list = data.get('paper_id_list')
    search_record = SearchRecord.objects.get(search_record_id=search_record_id)
    papers = []
    for paper_id in paper_id_list:
        paper = Paper.objects.get(paper_id=paper_id)
        papers.append(paper)
    search_record.related_papers.clear()
    for paper in papers:
        search_record.related_papers.add(paper)
        
    ### 修改知识库
    try: 
        kb_id = build_abs_kb_by_paper_ids(paper_id_list, search_record_id)
        insert_search_record_2_kb(search_record_id, kb_id)
    except Exception as e:
        return reply.fail(msg="构建知识库失败")
    
    return JsonResponse({'msg': '修改成功'}, status=200)

@require_http_methods(["DELETE"])
def flush(request):
    '''
    这是用来清空对话记录的函数
    :param request: 请求，类型为DEL
        内容包含：{
            search_record_id : string
        }
    '''
    username = request.session.get('username')
    data = json.loads(request.body)
    sr = SearchRecord.objects.get(search_record_id=data.get('search_record_id'))
    if sr is None:
        return JsonResponse({'error': '搜索记录不存在'}, status=404)
    else:
        conversation_path = sr.conversation_path
        import os
        if os.path.exists(conversation_path):
            os.remove(conversation_path)
        sr.delete()
        HttpRequest('清空成功', status=200)

