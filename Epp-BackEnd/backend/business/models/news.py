from django.db import models
import uuid
from datetime import datetime

class News(models.Model):
    """便于后续维护"""
    class CategoryChoices(models.TextChoices):
        AI = "AI", "人工智能（AI）"
        ML = "ML", "机器学习"
        CV = "CV", "计算机视觉与模式识别"
        NLP = "NLP", "自然语言处理"
        CRYPTO = "CR", "密码学与安全"
        SE = "SE", "软件工程"
        DISTRIBUTED = "DC", "分布式与并行计算"
        HCI = "HC", "人机交互"
    news_id = models.CharField(max_length=50, primary_key=True, verbose_name="news ID")  # 示例: "2505.14689v1"
    title = models.CharField(max_length=300, verbose_name="标题")  # 预留超长标题空间
    authors = models.TextField(verbose_name="作者列表")  # 改用Text存储可能很长的作者列表
    summary = models.TextField(verbose_name="总结")
    published = models.DateTimeField(verbose_name="发布时间")
    publish_date = models.DateField(verbose_name="发布日期")
    link = models.URLField(max_length=512, verbose_name="原文链接")
    rss_source = models.CharField(max_length=50, choices=CategoryChoices.choices, verbose_name="来源分类")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")

    """数据库配置"""
    class Meta:
        verbose_name = "arXiv论文"
        verbose_name_plural = "arXiv论文库"
        indexes = [
            models.Index(fields=['publish_date']),  # 按日期查询的索引
            models.Index(fields=['rss_source']),    # 按分类查询的索引
        ]
        ordering = ['-published']

    def __str__(self):
        return f"[{self.news_id}] {self.title[:50]}..."