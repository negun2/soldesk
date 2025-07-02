# onpremweb/community/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    AnalysisViewSet, BoardViewSet, RecommendViewSet, FeedbackViewSet,
    BestBoardViewSet, NoticeViewSet, ReplyViewSet, ScoreViewSet, ErrorLogViewSet, 
    RegisterView, current_user
)
from .views import BoardImageUploadView


router = DefaultRouter()
router.register(r'analysis', AnalysisViewSet)
router.register(r'boards', BoardViewSet)
router.register(r'recommends', RecommendViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'bestboards', BestBoardViewSet, basename='bestboard')
router.register(r'notices', NoticeViewSet)
router.register(r'replies', ReplyViewSet)
router.register(r'scores', ScoreViewSet)
router.register(r'errors', ErrorLogViewSet)

urlpatterns = [
    #path('api/', include(router.urls)),
    path('boards/upload/', BoardImageUploadView.as_view(), name='board-image-upload')    
    *router.urls,
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', current_user, name='current_user'),  # /api/me/
]
