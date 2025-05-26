from django.db import transaction
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
        response = requests.get(feed_url, headers=headers, timeout=20)
        response.raise_for_status()
        return feedparser.parse(response.content), None
    except Exception as e:
        return None, str(e)

from django.utils.timezone import make_naive

def _parse_entry(entry, feed_title):
    """统一数据解析格式"""
    published_str = entry.get('published', datetime.now().isoformat())
    dt_utc = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=UTC)
    beijing_time = dt_utc.astimezone(timezone("Asia/Shanghai"))
    naive_time = make_naive(beijing_time)
    return {
        'title': entry.get('title', 'Untitled'),
        'link': entry.get('link', ''),
        'published': naive_time, # beijing_time,  # 完整时间（带时区）
        'publish_date': beijing_time.date(),
        'summary': entry.get('summary', ''),
        'source': feed_title,
        "id": entry.get('id', ''),
        'authors': ', '.join(author.get('name', '') for author in entry.get('authors', []))
            # 'timestamp': datetime.now().isoformat()
    }

# @require_http_methods("POST")
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
            for entry in parsed.entries: # [:20]: # 可以限制每个分类最多20条数据，主要是避免太多了，用户看着繁杂。
                paper_data = _parse_entry(entry, category)

                if not News.objects.filter(news_id=paper_data['id']).exists():
                    abstract_start = paper_data['summary'].find("Abstract:")
                    if abstract_start != -1:
                        abstract = paper_data['summary'][abstract_start:]
                    else:
                        abstract = paper_data['summary']
                    News.objects.create(
                        news_id=paper_data['id'],
                        title=paper_data['title'],
                        authors=paper_data['authors'],
                        summary=abstract,
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
                abstract_start = paper_data['summary'].find("Abstract:")
                if abstract_start != -1:
                    abstract = paper_data['summary'][abstract_start:]
                else:
                    abstract = paper_data['summary']
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
    # days = int(request.GET.get('days', 1))
    # category = request.GET.get('category')

    # 获取当前日期和星期信息
    today = datetime.now().date()
    current_day_of_week = datetime.now().weekday()  # 0是周一，6是周日

    # 如果今天不是周六周日，检查是否有当天的新闻
    if current_day_of_week < 5:  # 周一到周五
        queryset_today = News.objects.filter(
            publish_date=today
        )
        if not queryset_today.exists():
            refresh(request)  # 如果没有当天数据，尝试刷新最新论文

    # 重新查询以确保数据最新，并获取近一周的全部新闻
    queryset = News.objects.filter(
        publish_date__gte=today - timedelta(days=7)
    ).order_by('-published')

    # if category:
    #     queryset = queryset.filter(rss_source=category)

    # 格式化查询结果，并添加time字符串
    papers = [{
        'id': paper.news_id,
        'title': paper.title,
        'published': paper.published.astimezone(timezone("Asia/Shanghai")).strftime("%m月%d日"),  # 转为"几月几日"
        'summary': paper.summary,
        'link': paper.link,
        'authors': paper.authors,
        'source': paper.rss_source,
        'time': _get_time_label(paper.published.astimezone(timezone("Asia/Shanghai")), today)
    } for paper in queryset]

    return success(
        data={
            'papers': papers,
            "count": len(papers)
        },
        msg="最新论文获取成功"
    )

def _get_time_label(published_date, today):
    """根据发布时间返回时间标签"""
    if published_date.date() == today:
        return "一天内"
    elif today - timedelta(days=3) <= published_date.date() < today:
        return "三天内"
    else:
        return "其他"

def get_latest_news_per_category():
    # 获取所有分类的唯一值
    categories = News.CategoryChoices.choices

    latest_news_list = []

    for category in categories:
        # 对于每个分类，获取最新的 5 篇新闻
        latest_news = News.objects.filter(rss_source=category[0]).order_by('-published')[:5]
        for news in latest_news:
            # 将每篇新闻转换为所需的字典格式
            latest_news_list.append({
                "title": news.title,
                "authors": news.authors,
                "summary": news.summary,
                "source": news.rss_source,
                "publish_date": news.published,
                # "published": news.published.strftime("%Y-%m-%d %H:%M:%S") if news.published else None,  # 格式化日期
                "link": news.link,
            })
    
    return latest_news_list

def generate_rss_summary(entries):

    # 不要出现markdown格式？

    prompt = f"""
请对以下最新学术论文或前沿新闻相关数据进行领域分类总结。
要求：
1. 划分领域类别
2. 每个领域单独建立总结板块
3. 每个领域总结需包括：
   - 近期研究趋势概述（2-3个方向）
   - 代表性成果简述（3项核心突破,注意说明成果来源论文标题）
   - 关键技术关键词列举
4. 使用学术化中文表达
5. 时间范围优先考虑最近7天的内容

输入数据格式示例：
{{
    title: '标题',
    authors: '作者',
    summary: '摘要文本',
    source: '来源',
    publish_date: '发表时间',
    link: '内容原文链接',
}},

现在开始处理以下论文数据：
{entries}   
"""
    from scripts.deepseek import queryDeepSeek
    from scripts.Kimi import queryKimi
    print("开始生成RSS总结")
    # summary = queryDeepSeek(prompt)
    summary = queryKimi(prompt)
    # 删除 # - ** 等 markdown 标记
    # summary = summary.replace("#", "").replace("- ", "").replace("**", "")
    return summary

@require_http_methods(["GET"])
def get_summary(request):
    summary = "无咨询可以总结"
    today = datetime.now().date()
    """查询今天最新论文"""
    queryset_today = News.objects.filter(
        publish_date=today
    )
    if not queryset_today.exists():
        refresh(request)

    # # 重新查询以确保数据最新，并获取近一周的全部新闻
    # queryset = News.objects.filter(
    #     publish_date__gte=today - timedelta(days=7)
    # ).order_by('-published')

    queryset = get_latest_news_per_category()
    summary = generate_rss_summary(queryset)

    return success(
        data={
            'summary': summary,
        },
        msg="最新总结已生成"
    )
