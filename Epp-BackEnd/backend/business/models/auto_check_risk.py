'''
自动审核所得不安全评论表
'''
from django.db import models
import uuid

from .auto_check_record import AutoCheckRecord

class AutoRiskRecord(models.Model):
    '''
    Field:
        - risk_record_id        不安全评论记录
        - check_record          自动审核记录
    '''
    risk_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    check_record = models.ForeignKey(AutoCheckRecord, on_delete=models.CASCADE)