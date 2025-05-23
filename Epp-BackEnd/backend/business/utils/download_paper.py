import requests
import os
import re
from urllib.parse import urlparse, urlunparse
# from backend.settings import PAPERS_PATH

# Clash代理配置（与您的配置文件对应）
CLASH_PROXY = {
    "http": "http://127.0.0.1:7890",   # HTTP代理端口
    "https": "http://127.0.0.1:7890",  # HTTPS代理端口
    "socks5": "socks5://127.0.0.1:7890" # SOCKS5代理端口
}

def downloadPaper(url, filename):
    # 预处理URL和文件名
    url = re.sub(r'^http://', 'https://', url, flags=re.IGNORECASE)
    parsed_url = urlparse(url)
    cleaned_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path.rstrip('/'),
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))

    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    save_path = os.path.join('resource/database/papers/', filename)
 
    # 文件已存在则直接返回路径
    if os.path.exists(save_path):
        is_valid, needs_repair = repair_pdf(save_path)
  
        return save_path
 
    try:
        # 使用Session保持连接（推荐用于多次请求）
        with requests.Session() as session:
            # 配置Clash代理
            session.proxies = {
                "http": CLASH_PROXY["http"],
                "https": CLASH_PROXY["https"]
            }
            # 配置重试和超时
            response = session.get(
                cleaned_url,
                stream=True,
                timeout=(10, 300),  # 连接超时10秒，读取超时300秒
                allow_redirects=True,  # 显式允许重定向
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept-Encoding': 'gzip, deflate'
                },
                verify=False  # 如果使用自签名证书需要设置
            )
            response.raise_for_status()  # 自动触发HTTPError异常
 
            # 写入文件（分块下载）
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤keep-alive块
                        f.write(chunk)
        
        return save_path
 
    except requests.exceptions.RequestException as e:
        # 打印详细错误信息（生产环境建议改用日志记录）
        print(f"[下载失败] URL: {cleaned_url} 错误: {str(e)}")
        # 可选：删除不完整的文件
        if os.path.exists(save_path):
            os.remove(save_path)
        return None

    except Exception as e:
        print(f"未知错误: {url}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return None
    
def check_proxy_connectivity():
    test_url = "https://api.ipify.org?format=json"
    try:
        response = requests.get(test_url, 
            proxies=CLASH_PROXY,
            timeout=5
        )
        print(f"当前出口IP: {response.json()['ip']}")
        return True
    except Exception as e:
        print(f"代理连接失败: {str(e)}")
        return False

# 运行验证
# check_proxy_connectivity()