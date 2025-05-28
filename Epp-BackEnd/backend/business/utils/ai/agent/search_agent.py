#该文件存储多智能体中的search_agent，用于在网络上检索相关信息，在scripts/tavily_test.py进行测试
from tavily import TavilyClient
from business.utils.ai.ai_settings import TAVILY_API_KEY

# 搜索引擎专家: Tavily (每月1000次免费调用)
tavily = TavilyClient(api_key=TAVILY_API_KEY)


def tavily_simple_search(query:str):
    query = query
    response = tavily.search(query)
    return response


# 高级搜索示例：限定arXiv并排除会议论文
def tavily_advanced_search(query:str):       
    response = tavily.search(
        query=query,
        search_depth="advanced",    # 深度搜索模式（覆盖更多数据库和PDF文献）
        max_results=5,             # 最大结果数量
        include_answer=True,        # 包含摘要
        include_raw_content=True,   # 获取原始网页内容
        include_images=False,       # 关闭无关图像
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

def get_search_reply(search_query): #获取tavily搜索引擎专家的结果
    search_list = tavily_advanced_search(search_query).get("results")

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