# 获取论文.py 文件开头添加以下代码
import os
import re

import django

# 设置环境变量（需替换为你的实际设置模块路径）
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.backend.settings")
django.setup()  # 初始化Django

from datetime import datetime
import json
import pprint
import random

from feedparser import FeedParserDict

import requests
import feedparser
import time
from urllib.parse import urlencode

from business.models import Paper


def fetch_arxiv_papers(target_year, max_results=100, retries=3):
    """
    获取指定年份的arXiv论文数据（带错误重试机制）

    :param target_year: 目标年份（字符串或整数）
    :param max_results: 单次请求最大结果数（建议<=100）
    :param retries: 请求失败重试次数
    :return: 论文数据列表，包含标题、作者、日期等信息
    """
    base_url = "http://export.arxiv.org/api/query?"
    papers = []
    start = 0
    total_results = None
    target_year = str(target_year)

    # 关键修复1：构造正确的日期范围查询（注意TO必须大写）
    search_query = f'submittedDate:[{target_year}0101600 TO {target_year}0102600]'

    # 关键修复2：添加必要的请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) arXivDataFetcher/1.0 (contact@example.com)"
    }

    while True:
        params = {
            "search_query": search_query,
            "start": start,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "ascending"
        }
        query_url = base_url + urlencode(params)

        # 关键修复3：带重试机制的请求
        for attempt in range(retries):
            try:
                response = requests.get(query_url, headers=headers, timeout=30)
                response.raise_for_status()  # 检查HTTP状态码
                break
            except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
                if attempt < retries - 1:
                    print(f"请求失败，第{attempt + 1}次重试... 错误：{str(e)}")
                    time.sleep(5)
                else:
                    print(f"请求失败，已达最大重试次数。最后错误：{str(e)}")
                    return []

        # 关键修复4：验证响应内容
        if response.status_code != 200:
            print(f"API返回异常状态码：{response.status_code}")
            print("响应内容前500字符：", response.text[:500])
            return []

        feed = feedparser.parse(response.content)

        # 关键修复5：检测解析错误
        if feed.bozo:
            print("XML解析错误！原始响应内容：")
            print(response.text[:1000])
            return []

        # 首次获取总结果数
        if total_results is None:
            try:
                total_results = int(feed.feed.opensearch_totalresults)
                print(f"找到{total_results}篇{target_year}年的论文")
                if total_results == 0:
                    print("可能原因：")
                    print("1. 日期范围错误（检查年份是否合理）")
                    print("2. 查询语法错误（已自动打印当前查询URL）")
                    print("当前查询URL:", query_url)
                    return []
            except AttributeError:
                print("无法获取总结果数，API响应结构可能已变更")
                print("建议检查原始响应内容：")
                print(response.text[:1000])
                return []

        # 提取论文数据
        current_batch = []
        for entry in feed.entries:
            # print_entry_raw(entry)
            # print(entry)
            try:
                paper_info = {
                    "title": entry.title.replace("\n", " ").strip(),
                    "authors": [author.name for author in entry.authors],
                    "published": entry.published,
                    "pdf_link": next(link.href for link in entry.links if (hasattr(link, 'title') and link.title == "pdf")),
                    "abstract": entry.summary.replace("\n", " ").strip()
                }
                current_batch.append(paper_info)
            except AttributeError as e:
                print(f"解析条目时出错（可能字段缺失），跳过该条目。错误：{str(e)}")

        papers.extend(current_batch)
        print(f"已获取 {len(papers)}/{total_results} 篇")

        # 更新分页索引
        start += max_results
        if start >= total_results:
            break

        # 遵守API速率限制
        time.sleep(3)

    return papers


def save_to_txt(papers, filename):
    """将论文数据保存到txt文件"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("{\n")
            f.write("   \"papers\": [\n")
            for idx, paper in enumerate(papers, 1):
                f.write("       {\n")
                f.write(f"          \"title\": \"{paper['title']}\",\n")
                f.write(f"          \"authors\": \"{', '.join(paper['authors'])}\",\n")
                f.write(f"          \"abstract\": \"{process_abstract_for_storage(paper['abstract'])}\",\n")
                f.write(f"          \"publication_date\": \"{paper['published']}\",\n")
                f.write(f"          \"citation_count\": 0,\n")
                f.write(f"          \"original_url\": \"{paper['pdf_link']}\"\n")
                f.write("       },\n")

                # f.write(f"论文 #{idx}\n")
                # f.write(f"标题: {paper['title']}\n")
                # f.write(f"作者: {', '.join(paper['authors'])}\n")
                # f.write(f"提交日期: {paper['published']}\n")
                # f.write(f"PDF链接: {paper['pdf_link']}\n")
                # f.write(f"摘要: {paper['abstract']}\n")
                # f.write("=" * 80 + "\n\n")

            f.write("   ]\n")
            f.write("}\n")
        print(f"成功保存 {len(papers)} 篇论文到 {filename}")
    except IOError as e:
        print(f"文件保存失败: {str(e)}")


def process_abstract_for_storage(text: str) -> str:
    """
    删除字符串中所有 LaTeX 格式内容，包括公式和命令，返回纯文本。

    功能说明：
    1. 删除所有被 `$...$` 或 `$$...$$` 包围的公式。
    2. 删除所有以反斜杠开头的 LaTeX 命令（如 `\textit{...}`、`\rm`）。
    3. 清理多余空格和换行符，确保文本连贯。

    :param text: 包含 LaTeX 的原始字符串
    :return: 清理后的纯文本
    """
    # 1. 删除所有被 $ 或 $$ 包围的公式内容（包括换行符）
    text = re.sub(r'\$+.*?\$+', '', text, flags=re.DOTALL)

    # 2. 删除所有 LaTeX 命令（如 \textit{...}、\rm）
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)  # 删除带花括号的命令及参数
    text = re.sub(r'\\[a-zA-Z]+\b', '', text)       # 删除无参数的单个命令（如 \rm）

    # 3. 删除所有剩余的反斜杠（如 $\cdot$ → $cdot$ 中的 \ 也会被删）
    text = re.sub(r'\\', '', text)  # 关键新增步骤

    text = re.sub(r'\'', '', text)  # 关键新增步骤
    text = re.sub(r'\"', '', text)  # 关键新增步骤

    # 4. 清理多余空格和换行符
    text = re.sub(r'\s+', ' ', text)   # 多个空格/换行符替换为单个空格
    text = text.strip()                # 移除首尾空格

    return text


def print_entry_raw(entry: FeedParserDict):
    """递归打印 FeedParserDict 对象的键值对"""

    def _format_value(value):
        if isinstance(value, FeedParserDict):
            # 递归处理嵌套的 FeedParserDict
            return {k: _format_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            # 处理列表中的每个元素
            return [_format_value(item) for item in value]
        else:
            return value

    # 将 FeedParserDict 转换为普通字典
    entry_dict = {key: _format_value(entry[key]) for key in entry.keys()}

    # 使用 pprint 打印结构化结果
    pprint.pprint(entry_dict, depth=4, width=120)

# 使用示例

# 测试查询（建议先测试有效年份）
# test_year = 2024  # 可改为2023等最新年份验证
#
# papers = fetch_arxiv_papers(test_year)
#
# if papers:
#     save_to_txt(papers, f"arxiv_papers_{test_year}.txt")
# else:
#     print("未获取到论文数据，请执行以下操作：")
#     print("1. 访问以下URL验证是否返回结果（替换为实际年份）")
#     print(
#         "   https://export.arxiv.org/api/query?search_query=submittedDate:[2020-01-01+TO+2020-12-31]&start=0&max_results=10&sortBy=submittedDate&sortOrder=ascending")
#     print("2. 检查控制台输出的错误信息")
#     print("3. 尝试更换网络环境（某些地区可能需要VPN）")

import json

# 读取文件内容
file_path = "arxiv_papers.txt"

try:
    Paper.objects.create(
        title='one page paper',
        authors='lin',
        abstract='This is a one page paper.',
        publication_date=datetime.strptime("2024-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ"),
        journal=None,  # 期刊允许为空，arXiv没有
        citation_count=0,
        original_url='',
        read_count=random.randint(0, 1000),
        like_count=0,
        collect_count=0,
        comment_count=0,
        download_count=random.randint(0, 1000)
    )
    # with open(file_path, "r", encoding="utf-8") as f:
    #     data = json.load(f)
    #     papers = data["papers"]  # 提取列表
    #     print(papers)
    #     for paper in papers:
    #         Paper.objects.create(
    #             title=paper['title'],
    #             authors=paper['authors'],
    #             abstract=paper['abstract'],
    #             publication_date=datetime.strptime(paper['publication_date'], "%Y-%m-%dT%H:%M:%SZ"),
    #             journal=None,  # 期刊允许为空，arXiv没有
    #             citation_count=paper['citation_count'],
    #             original_url=paper['original_url'],
    #             read_count=random.randint(0, 1000),
    #             like_count=0,
    #             collect_count=0,
    #             comment_count=0,
    #             download_count=random.randint(0, 1000)
    #         )

except FileNotFoundError:
    print(f"错误：文件 {file_path} 不存在")
except Exception as e:
    print(f"未知错误：{str(e)}")
