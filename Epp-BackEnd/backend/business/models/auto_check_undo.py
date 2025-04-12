'''
自动审核失败表
'''
from django.db import models
import uuid

from . import FirstLevelComment, SecondLevelComment
from .auto_check_record import AutoCheckRecord

class AutoUndoRecord(models.Model):
    '''
    Field:
        - undo_record_id        未成功自动审核的记录
        - comment_1             一级评论
        - comment_2             二级评论
        - comment_level         评论等级
    '''
    undo_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    comment_1 = models.ForeignKey(FirstLevelComment, on_delete=models.CASCADE, null=True, blank=True)
    comment_2 = models.ForeignKey(SecondLevelComment, on_delete=models.CASCADE, null=True, blank=True)
    comment_level = models.IntegerField(default=1)  # 1代表一级评论，2代表二级评论
