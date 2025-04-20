"""
平台文献私有笔记表
"""

from django.db import models
import uuid

from .user import User
from .paper import Paper

class FileNote(models.Model):
    """
    Field:
        - note_id               笔记ID
        - user_id               用户ID
        # - document_id           用户文件ID
        - paper_id              论文ID
        - date                  笔记创建时间

        - x                     x坐标
        - y                     y坐标
        - width                 宽
        - height                高
        - pageNum               笔记所在页数
        - comment               笔记内容
        - username              用户名
        - isPublic              是否公开
    """
    note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # document_id = models.ForeignKey(UserDocument, on_delete=models.CASCADE, null=True, blank=True)
    paper_id = models.ForeignKey(Paper, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)

    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    pageNum = models.IntegerField(default=1)
    comment = models.TextField(default="")
    username = models.CharField(max_length=255)
    isPublic = models.BooleanField(default=False)

