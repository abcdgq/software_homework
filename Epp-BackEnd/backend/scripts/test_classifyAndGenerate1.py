import json
import os
import django
import openai


server_ip = '115.190.109.233'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'
openai.api_base = f'http://{server_ip}:20005/v1'
openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"

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

        response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )

        if response.choices[0].message.role == "assistant":
            print(response.choices[0].message.content)
            result = json.loads(response.choices[0].message.content)
            return_result.append(result)

    return return_result

def test_localvdb_and_scholarapi(text):
    # from google_scholar_test import search_scholar
    # result_from_scholarapi = search_scholar(text)
    
    # standardized_result = devide_paper_in_scholarapi(result_from_scholarapi)
    standardized_result = []

    from business.utils.paper_vdb_init import get_filtered_paper
    result_from_localvdb = get_filtered_paper(text, 2)

    from .text_summary import text_summarizer #对查找的结果进行summarize，减少字节数，避免后续喂给ai时产生字符过多的错误
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

if __name__ == '__main__':
    # 设置环境变量指向你的 Django settings 模块
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    # 初始化 Django
    django.setup()
    print(test_localvdb_and_scholarapi("VQ-VAE"))
