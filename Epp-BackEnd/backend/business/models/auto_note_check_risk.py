'''
自动审核所得不安全评论表
'''
from django.db import models
import uuid

from .auto_note_check_record import AutoNoteCheckRecord


class AutoNoteRiskRecord(models.Model):
    '''
    Field:
        - risk_record_id        不安全评论记录
        - check_record          自动审核记录
    '''
    risk_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    check_record = models.ForeignKey(AutoNoteCheckRecord, on_delete=models.CASCADE)