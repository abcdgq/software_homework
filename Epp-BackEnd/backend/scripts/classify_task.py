import openai
from typing import Dict, Tuple, List
import json

server_ip = '115.190.109.233'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'
openai.api_base = f'http://{server_ip}:20005/v1'
openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"


# 定义任务类型
class Task:
    def __init__(self, description: str, task_type: str):
        self.description = description  # 任务描述
        self.type = task_type  # 任务类型: "query", "summarize", "study"

    def __str__(self):
        return f"{self.type.upper()}任务: {self.description}"


def decompose_user_input(user_input: str) -> List[Task]:
    """
    将用户输入分解为一系列任务
    返回: Task对象列表
    """
    prompt = f"""请将以下用户输入分解为一系列具体任务，并为每个任务分类:
用户输入: "{user_input}"

任务类型说明:
1. 查询任务(query): 需要查找特定信息或数据的问题
2. 总结任务(summarize): 需要对已有信息进行归纳总结的任务
3. 研读任务(study): 需要深入理解和分析复杂内容的任务

请按以下JSON格式回答，不要包含其他内容:
{{
    "analysis": "简短分析用户输入的任务组成",
    "tasks": [
        {{
            "description": "任务1描述",
            "type": "query/summarize/study"
        }},
        {{
            "description": "任务2描述",
            "type": "query/summarize/study"
        }}
    ]
}}"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        if response.choices[0].message.role == "assistant":
            result = json.loads(response.choices[0].message.content)
            return [Task(task['description'], task['type']) for task in result['tasks']]
    except Exception as e:
        print(f"任务分解出错: {e}")

    # 如果分解失败，返回默认任务(整个输入作为一个任务，尝试自动分类)
    return [Task(user_input, classify_single_task(user_input))]


def classify_single_task(task_description: str) -> str:
    """
    对单个任务进行分类
    返回: "query", "summarize" 或 "study"
    """
    prompt = f"""请对以下任务进行分类:
任务: "{task_description}"

分类选项:
1. query - 需要查找特定信息或数据的问题
2. summarize - 需要对已有信息进行归纳总结的任务
3. study - 需要深入理解和分析复杂内容的任务

请只返回分类结果(query/summarize/study)，不要包含其他内容。"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        if response.choices[0].message.role == "assistant":
            classification = response.choices[0].message.content.strip().lower()
            if classification in ['query', 'summarize', 'study']:
                return classification
    except Exception as e:
        print(f"任务分类出错: {e}")

    # 默认分类
    return "study"


def format_task_list(tasks: List[Task]) -> str:
    """格式化任务列表显示"""
    return "\n".join([f"{i + 1}. {task}" for i, task in enumerate(tasks)])


if __name__ == "__main__":
    history = []
    while True:
        user_input = input("用户：")
        if user_input.lower() == "exit":
            break

        # 1. 分解用户输入为多个任务
        tasks = decompose_user_input(user_input)
        print(f"\n[任务分解结果]\n{format_task_list(tasks)}\n")

        # 2. 处理每个任务
        for task in tasks:
            print(f"\n正在处理: {task}")

            # 根据任务类型调用不同的处理逻辑
            if task.type == "query":
                print("→ 这是一个查询任务，将使用学术搜索引擎")
                # 这里可以添加查询任务的处理代码
                from google_scholar_test import advanced_search
                results = advanced_search(user_input)
                print("学术专家结果:", results)
            elif task.type == "summarize":
                print("→ 这是一个总结任务，将逐步生成综述报告")
                # 这里可以添加总结任务的处理代码
                history.append({"role": "user", "content": task.description})
                try:
                    response = openai.ChatCompletion.create(
                        model=model,
                        messages=history,
                        stream=False
                    )
                    if response.choices[0].message.role == "assistant":
                        print(f"{model}: {response.choices[0].message.content}")
                        history.append({"role": "assistant", "content": response.choices[0].message.content})
                except Exception as e:
                    print(f"summarize出错: {e}")

            elif task.type == "study":
                print("→ 这是一个研读任务，将结合搜索引擎和LLM专家共同处理")
                # 这里可以添加研读任务的处理代码