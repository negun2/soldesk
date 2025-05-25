from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from community.views import signup, post_list
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', post_list, name='home'),
    path('admin/',       admin.site.urls),
    path('signup/',      signup,   name='signup'),
    path('community/', include('community.urls')),
    path('login/',       auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/',      auth_views.LogoutView.as_view(next_page='home'),        name='logout'),
]
