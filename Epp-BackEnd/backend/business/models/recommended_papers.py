"""
推荐文献
"""
from django.db import models
import uuid
from business.models import Paper

from business.utils import storage
from .subclass import Subclass

class RecomendedPaper(models.Model):
    """
    Field:
        - paper             文献
        - recommend_score   推荐指数
    """
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    recommend_score = models.FloatField(default=0.0)