from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from community.views import signup
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin/',       admin.site.urls),
    path('signup/',      signup,   name='signup'),
    path('community/', include('community.urls')),
    path('login/',       auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/',      auth_views.LogoutView.as_view(next_page='home'),        name='logout'),
    #path('test', TemplateView.as_view(template_name='index.html'), name='home'),
]
