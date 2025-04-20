"""
批注举报审核表
"""
from django.db import models
import uuid

from . import FileAnnotation
from .user import User


class AnnotationReport(models.Model):
    """
    Field:
        - annotation        批注
        - user              用户
        - date              举报时间
        - content           举报内容
        - judgment          处理意见
        - processed         举报完成情况
    """
    report_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    annotation = models.ForeignKey(FileAnnotation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.TextField(null=True, blank=True)
    judgment = models.TextField(deafult='', null=True, blank=True)
    processed = models.BooleanField(default=False)
