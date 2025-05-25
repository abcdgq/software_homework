import requests
import os
from urllib.parse import urlparse, urlunparse  # 用于安全处理URL
from backend.settings import PAPERS_PATH
import re

if not os.path.exists(PAPERS_PATH):
    os.makedirs(PAPERS_PATH)


def downloadPaper(url, filename):
    """
    下载文献到服务器
    """
    # path = os.path.join(PAPERS_PATH, filename) if filename.endswith('.pdf') else os.path.join(PAPERS_PATH, filename + '.pdf')
    # if os.path.exists(path):
    #     return path
    # response = requests.get(url)
    # if response.status_code == 200:
    #     print(filename)
    #     if not filename.endswith('.pdf'):
    #         filepath = os.path.join(PAPERS_PATH, filename + '.pdf')
    #     else:
    #         filepath = os.path.join(PAPERS_PATH, filename)
    #     with open(filepath, 'wb') as f:
    #         f.write(response.content)
    #     return filepath
    # else:
    #     print('下载失败')
    #     return None
    
    # # 确保路径存在
    # os.makedirs(PAPERS_PATH, exist_ok=True)

    # # 处理文件名
    # if not filename.endswith('.pdf'):
    #     filename += '.pdf'
    # path = os.path.join(PAPERS_PATH, filename)

    # # 检查文件是否已存在
    # if os.path.exists(path):
    #     return path

    # try:
    #     # 流式下载（避免超时和内存问题）
    #     response = requests.get(url, stream=True, timeout=30)
    #     response.raise_for_status()  # 检查 HTTP 错误

    #     with open(path, 'wb') as f:
    #         for chunk in response.iter_content(chunk_size=8192):
    #             if chunk:
    #                 f.write(chunk)
    #     return path
    # except requests.exceptions.RequestException as e:
    #     print(f'下载失败: {e}')
    #     return None
    
    # 安全处理URL（移除末尾斜杠）
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
    print("cleaned_url:")
    print(cleaned_url)

    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    save_path = os.path.join('resource/database/papers/', filename)
 
    # 文件已存在则直接返回路径
    if os.path.exists(save_path):
        return save_path
 
    try:
        # 使用Session保持连接（推荐用于多次请求）
        with requests.Session() as session:
            # 配置重试和超时
            response = session.get(
                cleaned_url,
                stream=True,
                timeout=(10, 300),  # 连接超时10秒，读取超时300秒
                allow_redirects=True,  # 显式允许重定向
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
