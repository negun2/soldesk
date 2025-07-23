# onpremweb_aws/community/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

class Notification(models.Model):
    NOTIFY_COMMENT = 'comment'
    NOTIFY_FEEDBACK_REPLY = 'feedback_reply'
    NOTIFY_NOTICE_REPLY = 'notice_reply'
    TYPE_CHOICES = [
        (NOTIFY_COMMENT, '댓글'),
        (NOTIFY_FEEDBACK_REPLY, '피드백댓글'),
        (NOTIFY_NOTICE_REPLY, '공지댓글'),
    ]
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey('Board', on_delete=models.CASCADE, null=True, blank=True)
    reply = models.ForeignKey('Reply', on_delete=models.CASCADE, null=True, blank=True)
    feedback = models.ForeignKey('Feedback', on_delete=models.CASCADE, null=True, blank=True)
    feedback_reply = models.ForeignKey('FeedbackReply', on_delete=models.CASCADE, null=True, blank=True)
    notice = models.ForeignKey('Notice', on_delete=models.CASCADE, null=True, blank=True)
    notice_reply = models.ForeignKey('NoticeReply', on_delete=models.CASCADE, null=True, blank=True)
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

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

class FeedbackImage(models.Model):
    feedback = models.ForeignKey(Feedback, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='feedbackImages/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

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
    created_at = models.DateTimeField(auto_now_add=True)

class NoticeImage(models.Model):
    notice = models.ForeignKey(Notice, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='noticeImages/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class NoticeReply(models.Model):
    notice = models.ForeignKey('Notice', related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Reply(models.Model):
    board = models.ForeignKey(Board, related_name='replies', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

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
    
