import openai
from typing import Dict, Tuple
import json

server_ip = '114.116.205.43'
url = f'http://{server_ip}:20005'
model = 'zhipu-api'
openai.api_base = f'http://{server_ip}:20005/v1'
openai.api_key = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"

# 专家模型权重类型
Weights = Dict[str, float]


def analyze_question_and_get_weights(user_input: str) -> Weights:
    """
    分析用户问题并返回三个专家模型的权重
    返回格式: {'scholar': 0-1, 'search': 0-1, 'llm': 0-1}
    """
    # 默认权重
    weights = {'scholar': 0.3, 'search': 0.3, 'llm': 0.4}

    # 构建提示词让大模型分析问题类型
    prompt = f"""请分析以下问题最适合哪种专家回答，并给出三种专家的权重(0-1之间，总和为1):
问题: "{user_input}"

请按以下JSON格式回答，不要包含其他内容:
{{
    "analysis": "简短分析问题类型",
    "weights": {{
        "scholar": 适合学术专家回答的程度(0-1),
        "search": 适合搜索引擎专家回答的程度(0-1),
        "llm": 适合通用大模型回答的程度(0-1)
    }}
}}"""

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )

        if response.choices[0].message.role == "assistant":
            result = json.loads(response.choices[0].message.content)
            return result['weights']
    except Exception as e:
        print(f"权重分析出错，使用默认权重: {e}")

    return weights


def decide_experts(weights: Weights, threshold: float = 0.4) -> Tuple[bool, bool, bool]:
    """
    根据权重决定使用哪些专家
    threshold: 阈值，超过此值则使用该专家
    返回: (use_scholar, use_search, use_llm)
    """
    return (
        weights['scholar'] >= threshold,
        weights['search'] >= threshold,
        weights['llm'] >= threshold
    )


def format_response(weights: Weights, decisions: Tuple[bool, bool, bool]) -> str:
    """
    格式化响应，显示权重和决策结果
    """
    scholar, search, llm = decisions
    return (
        f"\n[专家分配结果]\n"
        f"学术专家权重: {weights['scholar']:.2f} {'✅' if scholar else '❌'}\n"
        f"搜索引擎权重: {weights['search']:.2f} {'✅' if search else '❌'}\n"
        f"通用大模型权重: {weights['llm']:.2f} {'✅' if llm else '❌'}\n"
    )


if __name__ == "__main__":
    history = []
    while True:
        user_input = input("用户：")
        if user_input.lower() == "exit":
            break

        # 1. 分析问题并获取权重
        weights = analyze_question_and_get_weights(user_input)

        # 2. 根据权重决定使用哪些专家
        decisions = decide_experts(weights)

        # 3. 显示分配结果
        print(format_response(weights, decisions))

        # 4. 根据决策调用相应专家
        if decisions[2]:  # 使用LLM
            history.append({"role": "user", "content": user_input})
            response = openai.ChatCompletion.create(
                model=model,
                messages=history,
                stream=False
            )
            if response.choices[0].message.role == "assistant":
                print(f"{model}: {response.choices[0].message.content}")
                history.append({"role": "assistant", "content": response.choices[0].message.content})

        if decisions[0]:  # 使用学术专家
            from google_scholar_test import advanced_search
            results = advanced_search(user_input)
            print("学术专家结果:", results)

        if decisions[1]:  # 使用搜索引擎
            from tavily_test import tavily_simple_search
            results = tavily_simple_search(user_input)
            print("搜索引擎结果:", results)