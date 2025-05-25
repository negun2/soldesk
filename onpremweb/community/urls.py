from django.urls import path
from .views import (
    PostListView, PostDetailView,
    PostCreateView, PostUpdateView, PostDeleteView
)

app_name = 'community'

urlpatterns = [
    path('', PostListView.as_view(), name='list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='detail'),
    path('post/new/', PostCreateView.as_view(), name='create'),
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='delete'),
]
