from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import feedparser
import requests
from datetime import datetime

from django.views.decorators.http import require_http_methods
from pytz import timezone, UTC

from business.utils.reply import success, fail


RSS_FEEDS = {
        "36氪": "https://36kr.com/feed",

        # "人工智能": "https://arxiv.org/rss/cs.AI",
        # "机器学习": "https://arxiv.org/rss/cs.LG",
        # "计算机视觉与模式识别": "https://arxiv.org/rss/cs.CV",
        # "自然语言处理": "https://arxiv.org/rss/cs.CL",
        # "密码学与安全": "https://arxiv.org/rss/cs.CR",
        # "软件工程": "https://arxiv.org/rss/cs.SE",
        # "分布式与并行计算": "https://arxiv.org/rss/cs.DC",
        # "人机交互": "https://arxiv.org/rss/cs.HC",
    }

def _fetch_rss(feed_url):
    """统一RSS获取方法"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(feed_url, headers=headers, timeout=15)
        response.raise_for_status()
        return feedparser.parse(response.content), None
    except Exception as e:
        return None, str(e)

def _parse_entry(entry, feed_title):
    """统一数据解析格式"""
    try:
        published_str = entry.get('published', datetime.now().isoformat())
        dt_utc = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=UTC)
        # 转换为北京时间（UTC+8）
        beijing_tz = timezone("Asia/Shanghai")
        dt_beijing = dt_utc.astimezone(beijing_tz)
        # 格式化为清晰字符串
        formatted_time = dt_beijing.strftime("%Y年%m月%d日 %H:%M:%S")
    except:
        formatted_time = entry.get('published', datetime.now().isoformat())
    return {
        'title': entry.get('title', 'Untitled'),
        'link': entry.get('link', ''),
        'published': formatted_time,
        'summary': entry.get('summary', ''),
        'source': feed_title,
        "id": entry.get('id', ''),
        'authors': ', '.join(author.get('name', '') for author in entry.get('authors', []))
        # 'timestamp': datetime.now().isoformat()
    }

@require_http_methods("GET")
def get_newest_paper(request):
    """处理分类查询请求（使用统一响应风格）"""
    # 检查分类参数
    # category = request.GET.get('category')
    # if not category:
    #     return fail(msg="缺少分类参数")

    # category = "自然语言处理"

    # # 检查分类是否存在
    # if category not in RSS_FEEDS:
    #     return fail(msg="分类不存在")

    all_entries = []

    for name, url in RSS_FEEDS.items():
        # 获取RSS数据
        parsed, error = _fetch_rss(url)
        if error or not parsed or parsed.bozo:
            print(f"⚠️ Error: {error}")
            continue
        if error:
            print()
            return fail(msg=f"获取数据失败: {error}")
        
        # print(f"获取到 {parsed} 分类的最新论文数据")
        # 解析数据
        entries = [_parse_entry(entry, name) for entry in parsed.entries]
        all_entries.append(entries)

        print(f"{name}: {len(entries)} entries")
    
    print("RSS订阅AI总结: ", generate_rss_summary(all_entries))

    # 返回成功响应
    return success(
        data={
            "papers": entries,
            "count": len(entries)
        },
        msg="最新论文获取成功"
    )

def generate_rss_summary(entries):

    # 修改调用

    prompt = f"""
请对以下最新学术论文或前沿新闻相关数据进行领域分类总结。
要求：
1. 划分领域类别
2. 每个领域单独建立总结板块
3. 每个领域总结需包括：
   - 近期研究趋势概述（2-3个方向）
   - 代表性成果简述（3项核心突破）
   - 关键技术关键词列举
4. 使用学术化中文表达
5. 时间范围优先考虑最近7天的内容

输入数据格式示例：
{{
    title: '标题',
    summary: '摘要文本',
    source: '来源',
    published: '发表时间',
    link: '内容原文链接',
    authors: '作者',
}},

现在开始处理以下论文数据：
{entries}   
"""
    from scripts.deepseek import queryDeepSeek
    # from scripts.Kimi import queryKimi
    print("开始生成RSS总结")
    summary = queryDeepSeek(prompt)
    # 删除 # - ** 等 markdown 标记
    # summary = summary.replace("#", "").replace("- ", "").replace("**", "")
    return summary