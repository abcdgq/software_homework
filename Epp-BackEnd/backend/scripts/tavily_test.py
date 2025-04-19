# pip install tavily-python
from tavily import TavilyClient
import json

# 搜索引擎专家: Tavily (每月1000次免费调用)
TAVILY_API_KEY = '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'
tavily = TavilyClient(api_key=TAVILY_API_KEY)


def tavily_simple_search(query:str):
    query = query
    response = tavily.search(query)
    return response


# 高级搜索示例：限定arXiv并排除会议论文
def tavily_advanced_search(query:str):
    query = str
        
    response = tavily.search(
        query=query,
        search_depth="advanced",    # 深度搜索模式（覆盖更多数据库和PDF文献）
        max_results=50,             # 最大结果数量
        include_answer=True,        # 包含摘要
        include_images=False        # 关闭无关图像
    )
    return response


# 利用 Tavily 高级搜索参数
def tavily_domain_search(query:str):
    response = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=50,
        include_domains=["sciencedirect.com", "nature.com"],    # 指定学术网站（如 ["arxiv.org", "springer.com", "ieee.org"]），缩小搜索范围。
        exclude_domains=["youtube.com"],                        # 排除低质量来源（如 ["wikipedia.org", "blogspot.com"]）。
        include_answer=True,
        include_raw_content=False  # 避免冗余内容
    )
    return response


# if __name__ == "__main__":
#     # 调用 Tavily 搜索
#     response = tavily_simple_search()
#     response = tavily_advanced_search()
#     response = tavily_domain_search()

#     # 格式化输出到终端
#     formatted_response = json.dumps(response, indent=4)
#     print(formatted_response) # 返回包含标题、URL、摘要的JSON结果

#     # 输出到 JSON 文件
#     with open("response.json", "w", encoding="utf-8") as file:
#         json.dump(response, file, indent=4, ensure_ascii=False)