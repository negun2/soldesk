# onpremweb/onprem_project_config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from community.views import current_user, token_obtain_pair_view, test_csrf_view
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from community.views import current_user, token_obtain_pair_view, test_csrf_view
from django.utils import timezone
from django.contrib.auth.models import User

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

urlpatterns = [
    path('api/', include('community.urls')),   # 반드시 SPA 라우팅보다 위에 위치
    path('admin/', admin.site.urls),

    # 인증 관련
    path('api/token/', token_obtain_pair_view, name='token_obtain_pair'),    
    path('api/me/', current_user, name='current_user'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/csrf-test/', test_csrf_view),

    # REST API 엔드포인트
    path('api-auth/', include('rest_framework.urls')),
]

# 미디어 서빙용(개발서버 한정) 추가
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# SPA 진입점. 반드시 마지막에 위치시켜야 함!
# 'api/'로 시작하지 않는 모든 요청에만 SPA fallback 적용
urlpatterns += [
    re_path(r'^(?!api/).*$', TemplateView.as_view(template_name='index.html'), name='spa'),
]
