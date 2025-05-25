from django.urls import path
from .views import post_list, post_detail, post_create, post_update, post_delete
from . import views

app_name = 'community'

urlpatterns = [
    path('',           post_list,   name='post_list'),
    path('new/',       post_create, name='post_create'),
    path('<int:pk>/',  post_detail, name='post_detail'),
    path('<int:pk>/edit/',   post_update, name='post_update'),
    path('<int:pk>/delete/', post_delete, name='post_delete'),
]
