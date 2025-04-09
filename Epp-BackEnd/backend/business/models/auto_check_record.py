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
        - check_record_id       不良评论自动审核记录
        - user_id               用户ID
        - comment_id_1          一级评论ID
        - comment_id_2          二级评论ID
        - comment_level         评论等级
    '''
    check_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_id_1 = models.ForeignKey(FirstLevelComment, on_delete=models.CASCADE, null=True, blank=True)
    comment_id_2 = models.ForeignKey(SecondLevelComment, on_delete=models.CASCADE, null=True, blank=True)
    comment_level = models.IntegerField(default=1)  # 1代表一级评论，2代表二级评论
