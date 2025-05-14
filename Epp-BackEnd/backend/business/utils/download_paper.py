# import requests
# import os
# import subprocess
# import logging
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# from pathlib import Path
# from backend.settings import PAPERS_PATH

# # 配置日志
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class PDFProcessor:
#     def __init__(self):
#         self.download_dir = Path(PAPERS_PATH)
#         self.download_dir.mkdir(parents=True, exist_ok=True)

#     def _validate_pdf(self, file_path):
#         """深度验证PDF结构"""
#         try:
#             # 基础头校验
#             with open(file_path, 'rb') as f:
#                 header = f.read(4)
#                 if header != b'%PDF':
#                     logger.error("无效PDF文件头")
#                     return False

#             # 使用qpdf进行专业验证
#             result = subprocess.run(
#                 ['qpdf', '--check', str(file_path)],
#                 capture_output=True,
#                 text=True,
#                 timeout=10
#             )
#             return "PDF is valid" in result.stdout
#         except subprocess.TimeoutExpired:
#             logger.error("PDF验证超时")
#             return False
#         except Exception as e:
#             logger.error(f"验证异常: {str(e)}")
#             return False

#     def _repair_pdf(self, file_path):
#         """使用Ghostscript修复PDF"""
#         try:
#             temp_path = file_path.with_name(file_path.stem + "_repaired.pdf")
            
#             # Ghostscript修复命令
#             cmd = [
#                 'gs', '-o', str(temp_path),
#                 '-sDEVICE=pdfwrite',
#                 '-dPDFSETTINGS=/prepress',
#                 '-dCompatibilityLevel=1.7',
#                 str(file_path)
#             ]
            
#             result = subprocess.run(
#                 cmd,
#                 check=True,
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 timeout=30
#             )
            
#             # 替换原文件
#             temp_path.replace(file_path)
#             logger.info("PDF修复成功")
#             return True
#         except subprocess.CalledProcessError as e:
#             logger.error(f"修复失败[code {e.returncode}]: {e.stderr.decode()}")
#             return False
#         except Exception as e:
#             logger.error(f"修复异常: {str(e)}")
#             return False

#     def _download_file(self, url, file_path):
#         """增强版下载核心"""
#         session = requests.Session()
        
#         # 强制HTTPS请求
#         if url.startswith('http://'):
#             url = url.replace('http://', 'https://', 1)
        
#         # 配置重试策略
#         retries = Retry(
#             total=5,
#             status_forcelist=[408, 429, 500, 502, 503, 504],
#             allowed_methods=['GET'],
#             backoff_factor=1
#         )
        
#         session.mount('http://', HTTPAdapter(max_retries=retries))
#         session.mount('https://', HTTPAdapter(max_retries=retries))

#         try:
#             with session.get(
#                 url,
#                 stream=True,
#                 timeout=(10, 300),
#                 headers={'User-Agent': 'Mozilla/5.0'}
#             ) as response:
#                 response.raise_for_status()
                
#                 # 内容类型验证
#                 content_type = response.headers.get('Content-Type', '')
#                 if 'application/pdf' not in content_type:
#                     raise ValueError(f"无效内容类型: {content_type}")

#                 # 分块下载
#                 with open(file_path, 'wb') as f:
#                     for chunk in response.iter_content(chunk_size=8192):
#                         if chunk:
#                             f.write(chunk)
                            
#                             # 实时头校验
#                             if f.tell() <= 4 and b'%PDF' not in chunk:
#                                 raise ValueError("无效PDF文件头")

#                 # 最终大小验证
#                 expected_size = int(response.headers.get('Content-Length', 0))
#                 actual_size = file_path.stat().st_size
#                 if expected_size > 0 and actual_size != expected_size:
#                     raise IOError(f"大小不匹配: {actual_size}/{expected_size}")

#                 return True
#         except Exception as e:
#             if file_path.exists():
#                 file_path.unlink()
#             raise

#     def download_with_repair(self, url, filename):
#         """完整下载流程"""
#         # 检查文件名
#         if not filename.endswith('.pdf'):
#             filename += '.pdf'
        
#         file_path = self.download_dir / filename
        
#         if os.path.exists(file_path):
#             return str(file_path)
        
#         print("file_path:" + str(file_path))
#         # try:
#         #     # 执行下载
#         #     logger.info(f"开始下载: {filename}")
#         #     self._download_file(url, file_path)

#         #     # 验证并修复
#         #     if not self._validate_pdf(file_path):
#         #         logger.warning("文件需要修复...")
#         #         if not self._repair_pdf(file_path):
#         #             raise RuntimeError("修复失败")
                
#         #         # 二次验证
#         #         # if not self._validate_pdf(file_path):
#         #         #     raise RuntimeError("修复后验证失败")

#         #     logger.info(f"下载完成: {file_path}")
#         #     return str(file_path)
            
#         # except Exception as e:
#         #     logger.error(f"下载失败: {str(e)}")
#         #     if file_path.exists():
#         #         try:
#         #             file_path.unlink()
#         #         except Exception as clean_error:
#         #             logger.error(f"清理失败: {str(clean_error)}")
#         #     return None

# 使用示例
# if __name__ == "__main__":
#     processor = PDFProcessor("/data/papers")
#     result = processor.download_with_repair(
#         "https://example.com/paper.pdf",
#         "research_paper.pdf"
#     )
#     print("最终结果:", result)

import requests
from backend.settings import PAPERS_PATH
import os
from urllib.parse import urlparse, urlunparse  # 用于安全处理URL
import logging
import re

# 配置日志记录
logger = logging.getLogger(__name__)

if not os.path.exists(PAPERS_PATH):
    os.makedirs(PAPERS_PATH)


def repair_pdf(file_path):
    """
    PDF文件结构修复函数
    返回修复结果：(是否有效, 是否需要修复)
    """
    try:
        with open(file_path, 'rb+') as f:  # 需要读写模式
            # 基础头校验 (前1024字节)
            header = f.read(1024)
            if not header.startswith(b'%PDF-'):
                print(f"无效PDF头: {file_path}")
                return False, False

            # 查找文件结尾
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            
            # 从后向前查找EOF标记（至少检查最后1KB）
            search_window = min(1024, file_size)
            f.seek(-search_window, os.SEEK_END)
            tail_data = f.read()
            
            # 查找最后一个%%EOF
            eof_pos = tail_data.rfind(b'%%EOF')
            if eof_pos == -1:
                print(f"未找到EOF标记: {file_path}")
                return False, True
            
            # 计算实际EOF位置
            actual_eof = file_size - search_window + eof_pos + 5  # 5是%%EOF长度
            if actual_eof < file_size:
                print(f"修复截断PDF: {file_path} 原大小:{file_size} 新大小:{actual_eof}")
                f.truncate(actual_eof)
                return True, True
                
            return True, False
            
    except Exception as e:
        print(f"PDF修复失败: {file_path} - {str(e)}")
        return False, False


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
    cleaned_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path.rstrip('/'),  # 移除路径末尾斜杠
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment
        )
    )
 
    # 处理文件名（自动添加.pdf扩展名）
    if not filename.lower().endswith('.pdf'):
        filename += '.pdf'
    save_path = os.path.join(PAPERS_PATH, filename)
 
    # 文件已存在则直接返回路径
    if os.path.exists(save_path):
        is_valid, needs_repair = repair_pdf(save_path)
        
        if not is_valid:
            if needs_repair:
                # 尝试二次修复（可能需要重新下载）
                print("尝试二次修复...")
                is_valid, _ = repair_pdf(save_path)
                
            if not is_valid:
                print(f"PDF验证失败: {save_path}")
                os.remove(save_path)
                return None
        else:
            print("pdf无需修复")
            
            
        return save_path
 
    try:
        # 使用Session保持连接（推荐用于多次请求）
        with requests.Session() as session:
            # 配置重试和超时
            response = session.get(
                cleaned_url,
                stream=True,
                timeout=(10, 300),  # 连接超时10秒，读取超时300秒
                allow_redirects=True  # 显式允许重定向
            )
            response.raise_for_status()  # 自动触发HTTPError异常
 
            # 写入文件（分块下载）
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # 过滤keep-alive块
                        f.write(chunk)
        
        is_valid, needs_repair = repair_pdf(save_path)
        
        if not is_valid:
            if needs_repair:
                # 尝试二次修复（可能需要重新下载）
                print("尝试二次修复...")
                is_valid, _ = repair_pdf(save_path)
                
            if not is_valid:
                print(f"PDF验证失败: {save_path}")
                os.remove(save_path)
                return None
 
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