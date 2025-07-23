# onpremweb_aws/community/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AnalysisViewSet, BoardViewSet, RecommendViewSet, BoardLikeView, FeedbackViewSet, FeedbackImageUploadView, FeedbackReplyViewSet,
    BestBoardViewSet, NoticeViewSet, ReplyViewSet, ScoreViewSet, ErrorLogViewSet, BoardImageUploadView, UserViewSet, 
    RegisterView, current_user, user_list, UserViewSet, NotificationViewSet, NoticeReplyViewSet, NoticeImageUploadView
)
from . import views
from django.utils import timezone
from .views_presigned import s3_presigned_upload

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # username으로 유저 찾아서 last_login 갱신
            username = request.data.get("username")
            try:
                user = User.objects.get(username=username)
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
            except User.DoesNotExist:
                pass
        return response

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)
router.register(r'users', UserViewSet)
router.register(r'analysis', AnalysisViewSet)
router.register(r'boards', BoardViewSet)
router.register(r'recommends', RecommendViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'feedback-replies', FeedbackReplyViewSet)
router.register(r'bestboards', BestBoardViewSet, basename='bestboard')
router.register(r'notices', NoticeViewSet)
router.register(r'notice-replies', NoticeReplyViewSet)
router.register(r'replies', ReplyViewSet)
router.register(r'scores', ScoreViewSet)
router.register(r'errors', ErrorLogViewSet)

urlpatterns = [
    path('s3-presigned-upload/', s3_presigned_upload, name='s3-presigned-upload'),
    path('boards/upload/', BoardImageUploadView.as_view(), name='board-image-upload'),
    path('boards/<int:pk>/like/', BoardLikeView.as_view(), name='board-like'),
    path('feedbacks/upload/', FeedbackImageUploadView.as_view(), name='feedback-image-upload'),
    path('notices/upload/', NoticeImageUploadView.as_view(), name='notice-image-upload'),    
    path('register/', RegisterView.as_view(), name='register'),
    path('users/list/', user_list, name='user-list'),
    path('user/check-username/', views.check_username, name='check-username'),
    path('user/check-email/', views.check_email),    
    path('me/', current_user, name='current_user'),
    *router.urls,  # 항상 마지막/콤마
]
