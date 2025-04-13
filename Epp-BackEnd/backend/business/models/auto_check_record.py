'''
评论内容自动审核记录表
'''
from django.db import models
import uuid

from .user import User
from .comment import FirstLevelComment, SecondLevelComment

class AutoCheckRecord(models.Model):
    '''
    Field:
        - check_record_id       自动审核记录
        - comment_1             一级评论
        - comment_2             二级评论
        - comment_level         评论等级
        - security              评论是否安全
        - labels                自动审核接口返回的标签
        - reason                自动审核接口返回的详细原因
        - date                  时间
    '''
    check_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    comment_1 = models.ForeignKey(FirstLevelComment, on_delete=models.CASCADE, null=True, blank=True)
    comment_2 = models.ForeignKey(SecondLevelComment, on_delete=models.CASCADE, null=True, blank=True)
    comment_level = models.IntegerField(default=1)  # 1代表一级评论，2代表二级评论
    security = models.BooleanField(default=False)
    lables = models.TextField(default="", null=True, blank=True)
    reason = models.JSONField(default=dict, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)