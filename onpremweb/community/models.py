# onpremweb/community/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Analysis(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    total_price = models.CharField(max_length=255)
    original_img = models.CharField(max_length=255)
    scratch_img = models.CharField(max_length=255)
    crushed_img = models.CharField(max_length=255)
    natural_img = models.CharField(max_length=255)
    analyze_date = models.DateField()
    analyze_datetime = models.DateTimeField()

    def __str__(self):
        return f"Analysis {self.id} by {self.user}"

class Board(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    content = models.TextField() 
    cost = models.CharField(max_length=255, blank=True, null=True)  
    recommend_count = models.IntegerField(default=0)
    post_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class BoardImage(models.Model):
    board = models.ForeignKey(Board, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='boardImages/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Recommend(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('board', 'user')  # 유저는 같은 글 좋아요 한 번만!

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    title = models.CharField(max_length=200)
    content = models.TextField()      
    created_at = models.DateTimeField(auto_now_add=True)

class FeedbackReply(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback_replies')
    comment = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class BestBoard(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    update_date = models.DateTimeField(auto_now=True)

class Notice(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

class Reply(models.Model):
    board = models.ForeignKey(Board, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Score(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class ErrorLog(models.Model):
    code = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
