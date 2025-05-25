from django.shortcuts import render, redirect
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required

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
