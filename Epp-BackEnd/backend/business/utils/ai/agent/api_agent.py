#该文件存储多智能体中的api_agent，用于检索论文，在scripts/google_scholar_test.py进行测试
import json
from serpapi import GoogleSearch
from business.utils.ai.llm_queries.queryGLM import queryGLM
from business.utils.ai.ai_settings import google_search_api_key

def serpapi_client():
    return GoogleSearch({
        "api_key": google_search_api_key,  # 替换为实际密钥
        "engine": "google_scholar",  # 指定搜索引擎
        "hl": "en",                 # 语言设置
        "num": 5                   # 返回结果数
    })

def search_scholar(query: str): #基本文献检索
    client = serpapi_client()
    client.params_dict.update({
        "q": query,
        "as_ylo": 2000,    # 起始年份
        "as_yhi": 2024      # 结束年份
    })
    return client.get_dict()

def advanced_search( 
    keyword: str,
    author: str = None,
    journal: str = None,
    min_citations: int = None
):                             #多条件高级检索
    query_parts = [f'"{keyword}"']
    if author:
        query_parts.append(f'author:"{author}"')
    if journal:
        query_parts.append(f'source:"{journal}"')
    if min_citations:
        query_parts.append(f'cites>={min_citations}')
    
    client = serpapi_client()
    client.params_dict.update({
        "q": " ".join(query_parts),
        "as_ylo": 2000,
        "as_yhi": 2024
    })
    return client.get_dict()

#以上三个方法是google_search的api调用方法，在scripts/google_scholar_test.py进行测试。
#下边的部分是用在多智能体流程中的方法，在scripts/test_classifyAndGenerate1 进行测试

def devide_paper_in_scholarapi(result_from_scholarapi):
    articles = result_from_scholarapi.get('organic_results')
    return_result = []
    for article in articles:
        prompt = f"""
请根据article的内容，按后边JSON的要求提取里边的信息，完成提取任务
提取不到的信息，填“无”
以下是aritcle的内容{article}
请按以下JSON格式回答，不要包含其他内容,不要有格式之外的语句回答:
{{
    "paper": 
        {{
            "title": “文献的题目”,
            "authors": “文献的作者，只需要写名字”,
            "abstract": “文献的摘要”,
            "publication_date": “文献的发表时间”,
            "journal": “文献发表的期刊”,
            "citation_count": “文献的被引次数”,
            "original_url": “文献的original_url”
        }}
}}"""

        result = json.loads(queryGLM(prompt))
        return_result.append(result)

    return return_result

def localvdb_and_scholarapi(text):
    # 这里因为google_scholar api的限制所以注掉，只用本地的RAG搜索即可
    # result_from_scholarapi = search_scholar(text)
    
    # standardized_result = devide_paper_in_scholarapi(result_from_scholarapi)
    standardized_result = []

    from business.utils.paper_vdb_init import get_filtered_paper
    result_from_localvdb = get_filtered_paper(text, 2)

    from business.utils.text_summarizer import text_summarizer #对查找的结果进行summarize，减少字节数，避免后续喂给ai时产生字符过多的错误
    for a in result_from_localvdb:
        pa = a.to_use()
        summary_pa = text_summarizer(str(pa))
        standardized_result.append(summary_pa)

    docs = []  #来源总结
    for r in result_from_localvdb:
        attr = r.to_use().get('paper')
        docs.append(attr.get('title') + "  " + attr.get('original_url')) #返回题目和文献下载地址

    #返回示例 ['StarVQA: Space-Time Attention for Video Quality Assessment  http://arxiv.org/abs/2108.09635v1', 
    # 'VAQF: Fully Automatic Software-Hardware Co-Design Framework for Low-Bit  Vision Transformer  http://arxiv.org/abs/2201.06618v2']
    return standardized_result, docs

def get_api_reply(api_query):#获取本地RAG以及google scholar api检索文献结果（google scholar api有使用限制，还是以本地RAG为主）
    return localvdb_and_scholarapi(api_query)