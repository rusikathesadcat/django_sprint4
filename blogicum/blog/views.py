from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.http import Http404

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post

User = get_user_model()


# === ТРИ ОТДЕЛЬНЫЕ ФУНКЦИИ СОГЛАСНО ТЗ ===

def get_published_posts():
    """Фильтрация постов: только опубликованные, с опубликованной категорией и датой <= текущей."""
    return Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )


def annotate_comment_count(post_queryset):
    """Добавляет к каждому посту количество связанных комментариев."""
    return post_queryset.annotate(comment_count=Count('comments'))


def paginate_queryset(request, queryset, per_page=10):
    """Возвращает одну страницу пагинатора для заданного QuerySet."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


# === VIEW-ФУНКЦИИ ===

def index(request):
    posts = get_published_posts().order_by('-pub_date')
    posts = annotate_comment_count(posts)
    page_obj = paginate_queryset(request, posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=id
    )
    # Проверка доступа: черновики и будущие посты видны только автору
    if (
        not post.is_published or
        (post.category and not post.category.is_published) or
        post.pub_date > timezone.now()
    ):
        if request.user != post.author:
            raise Http404

    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    posts = get_published_posts().filter(category=category).order_by('-pub_date')
    posts = annotate_comment_count(posts)
    page_obj = paginate_queryset(request, posts)
    return render(request, 'blog/category.html', {'page_obj': page_obj, 'category': category})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    # В профиле показываем ВСЕ посты автора (включая неопубликованные)
    posts = Post.objects.filter(author=user).order_by('-pub_date')
    posts = annotate_comment_count(posts)
    page_obj = paginate_queryset(request, posts)
    return render(request, 'blog/profile.html', {'profile': user, 'page_obj': page_obj})


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = UserForm(instance=user)
    return render(request, 'blog/user.html', {'form': form})


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': PostForm(instance=post)})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'blog/comment.html', {'form': form, 'comment': comment})


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/comment.html', {'comment': comment})


def registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registration_form.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('blog:index')