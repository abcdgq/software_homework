from zhipuai import ZhipuAI

import requests

API_KEY = "adadd89573e44bbcab20a88177aef2af.rk3feklpIYygkLPZ"
url = "https://open.bigmodel.cn/api/paas/v4/embeddings"

payload = {
    "model": "text_embedding",
    "input": ["健康检查文本"],
    "encoding_format": "float",
    "text_type": "document"
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers, timeout=10)
print(f"状态码: {response.status_code}")
print(f"响应时间: {response.elapsed.total_seconds()}秒")
print(f"响应体: {response.text[:200]}...")

if __name__ == "__main__":
    
    client = ZhipuAI(api_key=API_KEY)
    response = client.embeddings.create(
        model="embedding-3",  # 模型名称需与API文档一致
        input=["测试文本"]
    )
    print(response.data[0].embedding[:5])  # 输出前5维向量值