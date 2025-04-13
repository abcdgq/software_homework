"""
用户笔记表
"""
from django.db import models
import uuid

from .user import User
from .paper import Paper
from .user_document import UserDocument

class FileNote(models.Model):
    """
    Field:
        - note_id               笔记ID
        - user_id               用户ID
        - document_id           用户文件ID
        - paper_id              论文ID
        - date                  笔记创建时间
        - public                是否公开
    """
    note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    document_id = models.ForeignKey(UserDocument, on_delete=models.CASCADE, null=True, blank=True)
    paper_id = models.ForeignKey(Paper, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
    public = models.BooleanField(default=True)
