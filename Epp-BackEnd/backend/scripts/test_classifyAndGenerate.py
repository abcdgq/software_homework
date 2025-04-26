import openai
from typing import Dict, Tuple, List
import json

server_ip = '115.190.109.233'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'
openai.api_base = f'http://{server_ip}:20005/v1'
openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"

if __name__ == '__main__':
    from classify_task import Task
    task = Task("解释VQ-VAE", "study")
    from tavily_test import tavily_simple_search, tavily_advanced_search, tavily_domain_search
    print(tavily_advanced_search(task.description))
    qa_list = tavily_advanced_search(task.description).get("results")
    uselist = []
    times = 0
    while True: #防止产生的结果过长，导致后边没法喂给大模型进行整合，进行一下筛选
        if times > 5: #防止问太多遍
            break
        for qa in qa_list:
            if qa['raw_content']:
                print(len(qa['raw_content']))
                if(len(qa['raw_content']) < 700):
                    uselist.append(qa)
            else:
                print(len(qa['content']))
                if(len(qa['content']) < 700):
                    uselist.append(qa)
        if len(uselist) >= 2:
            break
        else: #数量不够就重新问，重新筛
            qa_list = tavily_simple_search(task.description + "len < 600").get("results")
            uselist = []

    
    tavily_result = "\n".join([
f"- [{qa['title']}] {(qa['content'] if qa['raw_content'] == None else qa['raw_content'])} score ：{qa['score']}"
        for qa in uselist
    ])
    result_from_search = "以下是搜索引擎专家的回答：\n"  + tavily_result
                
    history_for_llm = []
    history_for_llm.append({"role": "user", "content": task.description + "\n生成结果的字符长度小于等于2000，且避免使用**加粗符号"})
    response = openai.ChatCompletion.create(
            model=model,
            messages=history_for_llm,
            stream=False
            )
    result = ""
    if response.choices[0].message.role == "assistant":
        result = response.choices[0].message.content
    result_from_llm = "\n以下是llm专家的回答：\n" + result
                
    results = result_from_search + result_from_llm
    task.result = results
    print(results)

    from gennerate_result import aggregate_answers
    child_qa_list = [task]
    print(aggregate_answers("解释VQ-VAE", search_reply=result_from_search, llm_reply=result_from_llm))