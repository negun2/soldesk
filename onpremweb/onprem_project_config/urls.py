# onpremweb/onprem_project_config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from community.views import current_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 인증 관련
    path('api/me/', current_user, name='current_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # REST API 엔드포인트
    path('api/', include('community.urls')),    # <-- 이거 하나면 됨!

    path('api-auth/', include('rest_framework.urls')),

    # SPA 진입점 (그 외 모든 URL)
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='spa'),
]
