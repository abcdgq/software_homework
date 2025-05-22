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
        "人工智能": "https://arxiv.org/rss/cs.AI",
        "机器学习": "https://arxiv.org/rss/cs.LG",
        "计算机视觉与模式识别": "https://arxiv.org/rss/cs.CV",
        "自然语言处理": "https://arxiv.org/rss/cs.CL",
        "密码学与安全": "https://arxiv.org/rss/cs.CR",
        "软件工程": "https://arxiv.org/rss/cs.SE",
        "分布式与并行计算": "https://arxiv.org/rss/cs.DC",
        "人机交互": "https://arxiv.org/rss/cs.HC",
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

def _parse_entry( entry, feed_title):
    """统一数据解析格式"""
    published_str = entry.get('published', datetime.now().isoformat())
    dt_utc = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=UTC)
    # 转换为北京时间（UTC+8）
    beijing_tz = timezone("Asia/Shanghai")
    dt_beijing = dt_utc.astimezone(beijing_tz)
    # 格式化为清晰字符串
    formatted_time = dt_beijing.strftime("%Y年%m月%d日 %H:%M:%S")
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
    category = "机器学习"

    # 检查分类是否存在
    if category not in RSS_FEEDS:
        return fail(msg="分类不存在")

    # 获取RSS数据
    parsed, error = _fetch_rss(RSS_FEEDS[category])
    if error:
        return fail(msg=f"获取数据失败: {error}")

    # 解析数据
    entries = [_parse_entry(entry, category) for entry in parsed.entries]

    # 返回成功响应
    return success(
        data={
            "papers": entries,
            "count": len(entries)
        },
        msg="最新论文获取成功"
    )