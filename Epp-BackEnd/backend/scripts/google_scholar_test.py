import json
from serpapi import GoogleSearch

def serpapi_client():
    return GoogleSearch({
        "api_key": "14ed0f506bb9d0e23dbd5b7816fed486ec32f4da50f37bf394aa3f7e3954e51d",  # 替换为实际密钥
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




if __name__ == '__main__':
    articles = advanced_search("deep learning")
    #articles_data = [article.model_dump() for article in articles]
    print(articles)
    # 写入JSON文件
    with open("test.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "results": articles
                },
                f,
                ensure_ascii=False,
                indent=2
            )