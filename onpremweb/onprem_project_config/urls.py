# onpremweb/onprem_project_config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from community.views import current_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static
from community.views import ( token_obtain_pair, test_csrf_view )

urlpatterns = [
    path('admin/', admin.site.urls),

    # 인증 관련
    path('me/', current_user, name='current_user'),
    path('token/', token_obtain_pair, name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('csrf-test/', test_csrf_view),

    # REST API 엔드포인트
    path('', include('community.urls')),   # 반드시 SPA 라우팅보다 위에 위치
    path('api-auth/', include('rest_framework.urls')),
]

# 미디어 서빙용(개발서버 한정) 추가
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# SPA 진입점. 반드시 마지막에 위치시켜야 함!
urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html'), name='spa'),
]
