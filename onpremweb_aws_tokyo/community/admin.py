# onpremweb/community/admin.py
from django.contrib import admin
from .models import (
    Analysis, Board, Recommend, Feedback, BestBoard,
    Notice, Reply, Score, ErrorLog
)

# Register Community app models with the admin site
admin.site.register(Analysis)
admin.site.register(Board)
admin.site.register(Recommend)
admin.site.register(Feedback)
admin.site.register(BestBoard)
admin.site.register(Notice)
admin.site.register(Reply)
admin.site.register(Score)
admin.site.register(ErrorLog)