'''
用于热门文献推荐，热门文献推荐基于用户的搜索历史，点赞历史，收藏历史
'''
from business.api.search import do_string_search
from business.api.user_info import collected_papers_list

# -*- coding: utf-8 -*-
"""
几乎所有推荐系统都是有着前后顺序的，但是我们的没有这些，这也就意味着我们的推荐系统是一个无状态的推荐系统
所以我选择了从arXiv上爬取最近一周的cv的每天10篇论文，然后通过总结这些论文的关键词，来进行推荐
"""

# 定时调用这个接口
# yourappname/tasks.py

from django_cron import CronJobBase, Schedule
from django.utils import timezone
from business.utils import reply
from business.models import Paper, SearchRecord, User
import random
random.seed(42)
import requests
# from bs4 import BeautifulSoup
# import arxiv
# from translate import Translator
# from tqdm import tqdm
import datetime
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
import json
import openai
from django.conf import settings
from business.api.summary import queryGLM


from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.views.decorators.http import require_http_methods
from business.utils.paper_vdb_init import get_filtered_paper

# server_ip = '114.116.205.43'
# url = f'http://{server_ip}:20005'
# model = 'zhipu-api'
# openai.api_base = f'http://{server_ip}:20005/v1'
# openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"

# def queryGLM(msg: str, history=None) -> str:
#     '''
#     对chatGLM3-6B发出一次单纯的询问
#     '''
#     print(msg)
#     chat_chat_url = 'http://172.17.62.88:7861/chat/chat'
#     headers = {
#         'Content-Type': 'application/json'
#     }
#     payload = json.dumps({
#         "query": msg,
#         "prompt_name": "default",
#         "temperature": 0.3
#     })
#
#     session = requests.Session()
#     retry = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#
#     try:
#         response = session.post(chat_chat_url, data=payload, headers=headers, stream=False)
#         response.raise_for_status()
#
#         # 确保正确处理分块响应
#         decoded_line = next(response.iter_lines()).decode('utf-8')
#         print(decoded_line)
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


class arxiv_paper:
    def __init__(self, title, summary, published, url, authors):
        self.title = title
        self.summary = summary
        self.published = published
        self.url = url
        self.authors = authors

    def __str__(self):
        return f"Title: {self.title}\nSummary: {self.summary}\nPublished: {self.published}\nURL: {self.url}\nAuthor: {self.authors}\n"

    def __dict__(self):
        author_str = ""
        for author in self.authors:
            author_str += author + ","
        return {
            "title": self.title,
            "summary": self.summary,
            "published": self.published,
            "url": self.url,
            "author": author_str
        }


def get_authors(entry):
    authors = []
    author_nodes = entry.findall('{http://www.w3.org/2005/Atom}author')
    for author_node in author_nodes:
        author_name = author_node.find('{http://www.w3.org/2005/Atom}name').text
        authors.append(author_name)
    return authors


def query_arxiv_by_date_and_field(start_date, end_date, field="computer vision", max_results=200) -> list[arxiv_paper]:
    query = f"submittedDate:[{start_date} TO {end_date}] AND all:{field}"
    url = f"http://arxiv.org/api/query?search_query={query}&id_list=&start=0&max_results={max_results}"
    response = requests.get(url)
    papers = []
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        total_results = root.find('.//{http://a9.com/-/spec/opensearch/1.1/}totalResults').text
        print(f"Total Results: {total_results}")
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            url = entry.find('{http://www.w3.org/2005/Atom}id').text
            authors = get_authors(entry)
            print('author:', authors)
            paper_instance = arxiv_paper(title, summary, published, url, authors)
            papers.append(paper_instance)
    else:
        print("Failed to fetch data.")
    return papers


def refreshCache():
    # 在这里写你想要执行的任务
    # 获取当前日期，以及前一周的日期
    today = datetime.now()
    last_week = today - timedelta(days=7)
    today_str = today.strftime("%Y-%m-%d")
    last_week_str = last_week.strftime("%Y-%m-%d")
    # 获取前一周的所有论文
    papers = []
    for i in range(7):
        start_date = (last_week + timedelta(days=i)).strftime("%Y-%m-%d")
        end_date = (last_week + timedelta(days=i + 1)).strftime("%Y-%m-%d")
        papers += query_arxiv_by_date_and_field(start_date, end_date)
    # 从中提取关键词
    keywords = []
    for paper in papers:
        msg = '这是一段关于' + paper.title + '的摘要，帮我总结三个关键词：' + paper.summary
        keywords.append(queryGLM(msg))

    # 从关键词中提取论文
    key = queryGLM(msg='帮我从这些关键词中提取出来十个关键词：' + ','.join(str(keywords)), history=[])
    
    papers = get_filtered_paper(key, k=10)
    # 将推荐数据缓存一天
    info = []
    for paper in papers:
        from business.models import Paper
        p = Paper.objects.get(paper_id=paper)
        info.extend(p.to_dict())
    cache.set('recommended_papers', info, timeout=86400)


from django.core.cache import cache


def get_recommendation(request):
    # 尝试从缓存中获取推荐数据
    cached_papers = cache.get('recommended_papers')
    if cached_papers:
        return reply.success(data={'papers': cached_papers}, msg='success')
    else:
        # 挂一个线程去刷新缓存
        import threading
        t = threading.Thread(target=refreshCache)
        t.start()
    # 从数据库中获取所有 Paper 对象的 ID
    papers_ids = list(Paper.objects.values_list('paper_id', flat=True))
    # 随机选择五篇论文的 ID
    selected_paper_ids = random.sample(papers_ids, min(10, len(papers_ids)))
    # 获取选中论文的详细信息
    selected_papers = []
    for paper_id in selected_paper_ids:
        paper = Paper.objects.get(paper_id=paper_id)
        selected_papers.append(paper)
    # 将选中的论文对象转换为字典
    papers = [paper.to_dict() for paper in selected_papers]
    # 将推荐数据缓存一天
    cache.set('recommended_papers', papers, timeout=86400)

    return reply.success(data={'papers': papers}, msg='success')



@require_http_methods(["GET"])
def get_unique_recommendation(request):
    username = request.session.get('username')
    user = User.objects.filter(username=username).first()

    search_record_list = SearchRecord.objects.filter(user_id=user)

    content = "["
    for record in search_record_list:
        content = content + record.keyword + ","
    content = content + "]"

    prompt = f"""
**任务说明**
你是一名学术文献推荐系统的智能分析引擎，需要根据用户的历史搜索记录生成精准的向量数据库查询词。请按以下步骤处理：

**输入数据**
用户历史搜索记录："{content}"

**处理要求**
1. 语义解构：
   - 识别核心研究领域（如：机器学习>图神经网络>药物研发）
   - 提取技术关键词（如：GNN、分子表征学习）
   - 分析潜在需求（如：方法比较/应用场景/理论突破）

2. 查询词生成

3. 输出规范：
   • 中英文混合术语（适应跨库检索）
   • 语义分层结构：
     [核心主题] > [技术方法] > [应用场景]
   • 排除非学术词汇（如"最佳实践"等模糊表述）
   • 生成10-15个检索词，按相关性降序排列

请严格按以下JSON格式回答，仅在中括号中填写内容，除了这个JSON内容以外不要回答任何其他内容:
{{
    "keywords": [keyword]
}}"""

    result = "{\"keywords\": []}"

    try:
        result = queryGLM(prompt)
        # print(result)
        # response = openai.ChatCompletion.create(
        #     model=model,
        #     messages=[{"role": "user", "content": prompt}],
        #     stream=False
        # )
        #
        # if response.choices[0].message.role == "assistant":
        #     result = json.loads(response.choices[0].message.content)
        #     keywords = result['keywords']
    except Exception as e:
        print(f"未能正确获得个性化推荐: {e}")

    count = 0

    keywords = json.loads(result)['keywords']
    # print(keywords)
    filtered_papers_list = []
    for keyword in keywords:
        # papers = do_string_search(keyword)
        papers = get_filtered_paper(keyword,4)
        # print('papers:', papers)
        count_keyword = 0
        for p in papers:
            # print(p.title)
            filtered_papers_list.append(p.to_dict())
            count = count + 1
            count_keyword = count_keyword + 1
            if count_keyword > 3:
                break
        if count > 20:
            break

    print(filtered_papers_list)

    return reply.success(data={'papers': filtered_papers_list}, msg='success')


@require_http_methods("GET")
def get_related_paper(request):
    # print("------------------------------------------------")
    # print(request.session.items())
    username = request.session.get('username')
    # print('recommend username:' + username)
    user = User.objects.filter(username=username).first()
    collected_papers_list = user.collected_papers.all()

    paper_id = request.GET.get('paper_id')
    paper = Paper.objects.filter(paper_id=paper_id).first()
    title = paper.title

    data = {
        'papers': []
    }
    
    # papers = get_filtered_paper(title, 5)
    papers = do_string_search(title, 5)
    papers = papers[1:]  # 去掉第一篇，因为是用户当前阅读的论文
    
#     prompt = f"""
    
# **角色：** 你是一位专业的学术研究员，精通文献分析和知识关联。你的任务是为文献推荐系统提供清晰、准确、有说服力的推荐理由。

# **背景：** 用户正在阅读一篇论文（论文 A）。文献推荐系统基于某种算法（如内容相似性、引用关系、主题模型、作者网络等）推荐了另一篇论文（论文 B）。现在需要你生成一段自然语言的解释，说明论文 B 为什么与论文 A 相关。

# **输入信息：**
# 1.  **论文 A (用户当前阅读的论文):**
#     {paper.to_dict()}
# 2.  **论文 B (被推荐的论文):**
#     {json.dumps(papers)}

# **任务要求：**
# 1.  **分析关联性：** 仔细比较论文 A 和论文 B 的标题、摘要、关键词和其他可用信息。找出它们之间最显著、最具体的关联点。可能的关联类型包括但不限于：
#     *   **研究主题/问题相似性：** 解决相同或高度相关的研究问题。
#     *   **方法论相似性/延续：** 使用相同、类似或改进的研究方法/技术/模型。
#     *   **理论基础/背景一致：** 基于相同的理论框架或共享核心概念。
#     *   **应用领域相同：** 应用于相同的具体领域（如医疗、金融、机器人）。
#     *   **引用关系：** 论文 B 引用了论文 A（或反之），或它们共同被许多其他论文引用（表明是领域基础）。
#     *   **作者关联：** 同一作者、同一实验室或紧密合作者。
#     *   **延续/扩展工作：** 论文 B 是论文 A 工作的直接延续、改进或应用。
#     *   **对比/替代方案：** 提出解决相同问题的不同方法（对比视角）。
# 2.  **生成解释：** 基于你的分析，撰写一段 **1-3 句** 简洁、自然、易懂的英文（或你需要的语言）解释，清晰地阐述论文 B 与论文 A 的核心关联点。
#     *   **具体化：** 避免泛泛而谈（如“都是关于AI的”）。明确指出具体的主题、方法、概念或关系。例如：“这篇论文提出了一个更高效的训练算法来解决论文 A 中提到的模型收敛慢的问题。”
#     *   **利用线索：** 如果提供了`推荐依据线索`，务必将其融入解释中，增加可信度。例如：“由于在主题模型计算中相似度得分高达 0.92，这篇论文探讨了与论文 A 非常相似的深度学习架构优化问题。” 或 “作为论文 A 的主要作者的最新工作，此论文扩展了原始模型的应用范围。”
#     *   **面向读者：** 语言应适合学术读者，清晰专业，避免过度技术性术语堆砌（除非你的用户群体非常专业）。
#     *   **聚焦核心：** 突出**最主要**的 1-2 个关联点，保持解释精炼。
# 3.  **输出格式：** 只输出生成的解释文本本身，不要包含额外的分析过程、标题或标记。例如：
#     `"这篇论文 (B) 采用了与论文 A 相同的基于 Transformer 的框架，但将其应用于 [具体领域 B]，验证了该框架在该领域的有效性，是论文 A 方法的重要扩展应用。"`
#     `"作为论文 A 的后续研究，此论文 (B) 深入分析了论文 A 中观察到的 [具体现象 X] 的内在机制，提供了更深入的理论解释。"`
#     `"论文 B 引用了论文 A 作为其 [具体理论/方法] 的基础，并在 [具体方面 Y] 上提出了显著的改进方案。"`

# **现在请生成推荐原因：**

# 1.  输出规范：
# 请严格按以下JSON格式回答，仅在中括号中填写内容，除了这个JSON内容以外不要回答任何其他内容:
# {
#     "reasons": [{
#         "paper_id": "论文 B 的 ID",
#         "reason": "推荐原因"
#     }]
# }
    
#     """

#     result = "{\"reasons\": []}"

#     try:
#         result = queryGLM(prompt)
#         print(result)
#     except Exception as e:
#         print(f"未能正确获得个性化推荐: {e}")
    
    # 定义字符串列表
    str_list = ["研究领域相近", "被引用", "研究领域有交叉", "可能感兴趣"]

    for p in papers:
        data['papers'].append({
            'id': str(p.paper_id),
            'title': p.title,
            'summary': random.choice(str_list),
            'collected': p in collected_papers_list
        })
    # print("data:")
    # print(data)
    return reply.success(data=data, msg='获取成功')