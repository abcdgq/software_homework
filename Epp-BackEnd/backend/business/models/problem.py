"""
用户搜索记录表
"""
from django.db import models
import uuid




from django.db import models

class problem_record(models.Model):
    """
    问题记录模型（用于计数统计）
    """
    content = models.TextField(null=True, blank=True, verbose_name="问题内容")
    number = models.PositiveIntegerField(default=0, verbose_name="出现次数")  # 计数字段

    class Meta:
        verbose_name = "问题记录"
        verbose_name_plural = verbose_name
        ordering = ["-number"]  # 按出现次数倒序排列

    def __str__(self):
        return f"问题：{self.content[:20]}（出现{self.number}次）"