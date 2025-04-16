'''
公开批注存储表
'''
from django.db import models
import uuid

from .note import FileNote
from .user import User
from .paper import Paper
from .user_document import UserDocument

class FileAnnotation(models.Model):
    """
    Field:
        - annotation_id         批注ID
        - note_id               笔记ID
        - user_id               用户ID
        # - document_id           用户文件ID
        - paper_id              论文ID
        - date                  笔记创建时间
    """
    annotation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    note = models.ForeignKey(FileNote, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    # document_id = models.ForeignKey(UserDocument, on_delete=models.CASCADE, null=True, blank=True)
    paper_id = models.ForeignKey(Paper, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)
