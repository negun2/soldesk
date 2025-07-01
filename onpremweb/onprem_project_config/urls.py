# onprem_project_config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from community import urls as community_urls
from community.views import (
    current_user,
    AnalysisViewSet, BoardViewSet, RecommendViewSet,
    FeedbackViewSet, BestBoardViewSet, NoticeViewSet,
    ReplyViewSet, ScoreViewSet, ErrorLogViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView,
)
from rest_framework.routers import DefaultRouter
from rest_framework import routers
from rest_framework.authtoken import views as drf_auth_views

# REST API 라우터 설정
router = DefaultRouter()
router.register(r'analysis', AnalysisViewSet, basename='analysis')
router.register(r'boards', BoardViewSet, basename='boards')
router.register(r'recommends', RecommendViewSet, basename='recommends')
router.register(r'feedbacks', FeedbackViewSet, basename='feedbacks')
router.register(r'bestboards', BestBoardViewSet, basename='bestboards')
router.register(r'notices', NoticeViewSet, basename='notices')
router.register(r'replies', ReplyViewSet, basename='replies')
router.register(r'scores', ScoreViewSet, basename='scores')
router.register(r'errors', ErrorLogViewSet, basename='errors')

urlpatterns = [
    path('admin/', admin.site.urls),
    # 인증 관련
    path('api/me/', current_user, name='current_user'),
    path('signup/', include('community.urls')),  # signup view는 community.urls 네임스페이스 안에 정의
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),


    # REST API 엔드포인트
    path('api/', include((router.urls, 'api'), namespace='api')),

    # 필요 시 기존 커뮤니티 서버 렌더링 앱
    path('community/', include((community_urls, 'community'), namespace='community')),

    # SPA 진입점 (그 외 모든 URL)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='spa'),
]
