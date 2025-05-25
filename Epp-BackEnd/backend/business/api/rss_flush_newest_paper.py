from django.db import transaction
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import feedparser
import requests
from datetime import datetime, timedelta

from django.views.decorators.http import require_http_methods
from pytz import timezone, UTC

from business.models.news import News
from business.utils.reply import success, fail


RSS_FEEDS = {
    "AI": "https://arxiv.org/rss/cs.AI",
    "ML": "https://arxiv.org/rss/cs.LG",
    "CV": "https://arxiv.org/rss/cs.CV",
    "NLP": "https://arxiv.org/rss/cs.CL",
    "CR": "https://arxiv.org/rss/cs.CR",
    "SE": "https://arxiv.org/rss/cs.SE",
    "DC": "https://arxiv.org/rss/cs.DC",
    "HC": "https://arxiv.org/rss/cs.HC",
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
    published_str = entry.get('published', datetime.now().isoformat())
    dt_utc = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=UTC)
    beijing_time = dt_utc.astimezone(timezone("Asia/Shanghai"))
    return {
        'title': entry.get('title', 'Untitled'),
        'link': entry.get('link', ''),
        'published': beijing_time,  # 完整时间（带时区）
        'publish_date': beijing_time.date(),
        'summary': entry.get('summary', ''),
        'source': feed_title,
        "id": entry.get('id', ''),
        'authors': ', '.join(author.get('name', '') for author in entry.get('authors', []))
            # 'timestamp': datetime.now().isoformat()
    }

@require_http_methods("POST")
def refresh(request):
    """处理分类查询请求（使用统一响应风格）"""
    result = False
    count = 0
    msg = ""
    # 检查分类参数
    for category, url in RSS_FEEDS.items():
        parsed, error = _fetch_rss(url)
        if error or not parsed or parsed.bozo:
            print(f"⚠️ Error: {error}")
            msg = error
            continue
        with transaction.atomic():
            result = True
            count = count + len(parsed.entries)
            for entry in parsed.entries:
                paper_data = _parse_entry(entry, category)

                if not News.objects.filter(news_id=paper_data['id']).exists():
                    News.objects.create(
                        news_id=paper_data['id'],
                        title=paper_data['title'],
                        authors=paper_data['authors'],
                        summary=paper_data['summary'],
                        published=paper_data['published'],  # UTC时间
                        publish_date=paper_data['publish_date'],  # 格式化时间
                        link=paper_data['link'],
                        rss_source=category,
                    )
    if not result:
        return fail(msg=f"获取数据失败: {msg}")

    if count == 0:
        return fail(msg=f"获取数据0个")
    # 返回成功响应
    return success(
        data={
            "count": count
        },
        msg="最新论文获取成功"
    )

def save_papers_to_db(category):
    parsed, error = _fetch_rss(RSS_FEEDS[category])
    if error or not parsed or parsed.bozo:
        print(f"⚠️ Error: {error}")
        return False

    with transaction.atomic():
        for entry in parsed.entries:
            paper_data = _parse_entry(entry, category)

            # 用news_id去重（避免重复存储）
            if not News.objects.filter(news_id=paper_data['id']).exists():
                News.objects.create(
                    news_id=paper_data['id'],
                    title=paper_data['title'],
                    authors=paper_data['authors'],
                    summary=paper_data['summary'],
                    published=paper_data['published'],  # UTC时间
                    publish_date=paper_data['publish_date'],  # 格式化时间
                    link=paper_data['link'],
                    rss_source=category,
                )
    return True


@require_http_methods(["GET"])
def get_news_by_days(request):
    """返回格式化日期（如`5月22日`）的论文列表"""
    days = int(request.GET.get('days', 1))
    category = request.GET.get('category')

    # 查询数据库
    queryset = News.objects.filter(
        publish_date__gte=datetime.now().date() - timedelta(days=days)
    ).order_by('-published')

    if category:
        queryset = queryset.filter(rss_source=category)
    papers = [{
        'id': paper.news_id,
        'title': paper.title,
        'published': paper.published.astimezone(timezone("Asia/Shanghai")).strftime("%m月%d日"),  # 转为"几月几日"
        'summary': paper.summary,
        'link': paper.link,
        'authors': paper.authors,
        'source': paper.rss_source,
    } for paper in queryset]

    return success(
        data={
            'papers': papers,
            "count": len(papers)
        },
        msg="最新论文获取成功"
    )