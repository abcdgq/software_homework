'''
笔记内容自动审核记录表
'''
from django.db import models
import uuid

from . import FileNote
from .user import User
from .comment import FirstLevelComment, SecondLevelComment

class AutoNoteCheckRecord(models.Model):
    '''
    Field:
        - check_record_id       自动审核记录
        - note                  笔记
        - security              评论是否安全
        - labels                自动审核接口返回的标签
        - reason                自动审核接口返回的详细原因
        - date                  时间
    '''
    check_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    note = models.ForeignKey(FileNote, on_delete=models.CASCADE, null=True, blank=True)
    security = models.BooleanField(default=False)
    labels = models.TextField(default="", null=True, blank=True)
    reason = models.JSONField(default=dict, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)