# onpremweb/community/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AnalysisViewSet, BoardViewSet, RecommendViewSet, BoardLikeView, FeedbackViewSet, FeedbackImageUploadView, FeedbackReplyViewSet,
    BestBoardViewSet, NoticeViewSet, ReplyViewSet, ScoreViewSet, ErrorLogViewSet, 
    RegisterView, current_user, user_list, UserViewSet
)
from .views import BoardImageUploadView


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'analysis', AnalysisViewSet)
router.register(r'boards', BoardViewSet)
router.register(r'recommends', RecommendViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'feedback-replies', FeedbackReplyViewSet)
router.register(r'bestboards', BestBoardViewSet, basename='bestboard')
router.register(r'notices', NoticeViewSet)
router.register(r'replies', ReplyViewSet)
router.register(r'scores', ScoreViewSet)
router.register(r'errors', ErrorLogViewSet)

urlpatterns = [
    path('boards/upload/', BoardImageUploadView.as_view(), name='board-image-upload'),
    path('boards/<int:pk>/like/', BoardLikeView.as_view(), name='board-like'),
    path('feedbacks/upload/', FeedbackImageUploadView.as_view(), name='feedback-image-upload'),    
    path('register/', RegisterView.as_view(), name='register'),
    path('users/list/', user_list, name='user-list'),    
    path('me/', current_user, name='current_user'),
    *router.urls,  # 항상 마지막/콤마
]
