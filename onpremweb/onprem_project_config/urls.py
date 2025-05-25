from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from community.views import signup
from django.contrib.auth import views as auth_views
from django.urls import include

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('admin/',       admin.site.urls),
    path('signup/',      signup,   name='signup'),
    path('login/',       auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/',      auth_views.LogoutView.as_view(next_page='home'),        name='logout'),
    path('community/', include('community.urls', namespace='community')),
]
