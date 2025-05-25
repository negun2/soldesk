from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView,
    CreateView, UpdateView, DeleteView
)

class PostListView(ListView):
    model = Post
    template_name = 'community/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

class PostDetailView(DetailView):
    model = Post
    template_name = 'community/post_detail.html'

class PostCreateView(CreateView):
    model = Post
    fields = ['title','content']
    form_class = PostForm
    template_name = 'community/post_form.html'
    success_url = reverse_lazy('community:list')

class PostUpdateView(UpdateView):
    model = Post
    fields = ['title','content']
    form_class = PostForm
    template_name = 'community/post_form.html'
    success_url = reverse_lazy('community:list')

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'community/post_confirm_delete.html'
    success_url = reverse_lazy('community:list')

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'community/post_list.html', {'posts': posts})

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'community/post_create.html', {'form': form})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')     # 가입 후 홈으로
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
