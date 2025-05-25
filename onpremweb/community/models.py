# onpremweb/community/models.py
from django.conf import settings
from django.db import models

class Post(models.Model):
    author     = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,         # ← allow NULL for now
        blank=True
    )
    title      = models.CharField(max_length=200)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
