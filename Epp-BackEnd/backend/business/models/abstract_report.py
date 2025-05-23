"""
摘要报告表
"""
from django.db import models
import uuid

from .user import User


class AbstractReport(models.Model):
    """
    Field:
        - file_local_path      文件本地地址
        - report_path          摘要报告文件地址
        - status               状态
    """
    
    STATUS_PENDING = 'P'
    STATUS_IN_PROGRESS = 'IP'
    STATUS_COMPLETED = 'C'
    STATUS_TIMEOUT = 'T'
    STATUS_CHOICES = [
        (STATUS_PENDING, '未生成'),
        (STATUS_IN_PROGRESS, '生成中'),
        (STATUS_COMPLETED, '已生成'),
        (STATUS_TIMEOUT, '超时')
    ]
    
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    file_local_path = models.CharField(max_length=255)
    report_path = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
