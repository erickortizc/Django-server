# models.py
from django.db import models

class MergeRequest(models.Model):
    nombreArchivo = models.CharField(max_length=255)
    urls = models.JSONField()