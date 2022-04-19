from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .settings import POSTS_ON_PAGE


def paginate(request, posts, posts_per_page=POSTS_ON_PAGE):
    """Функция пагинации"""
    return Paginator(posts, posts_per_page).get_page(request.GET.get('page'))

def index(request):
    """View-функция для главной страницы"""
    # print('Вызов вью для индекса')
    return render(request, 'posts/index.html', {
        'page_obj': paginate(request, Post.objects.all())
    })


def group_posts(request, slug):
    """View-функция для страницы с лентой группы"""
    group = get_object_or_404(Group, slug=slug)
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': paginate(request, group.posts.all())
    })


def profile(request, username):
    """View-функция для страницы с лентой профиля"""
    author = get_object_or_404(User, username=username)
    following = request.user.is_authenticated and (
        Follow.objects.filter(
            user=request.user
        ).filter(
            author=author
        ).exists()
    )
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': paginate(request, author.posts.all()),
        'following': following
    })


def post_detail(request, post_id):
    """View-функция для страницы подробной информации о посте"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments,
    })


@login_required
def post_create(request):
    """View-функция для создания поста"""
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    """View-функция для редактирования поста"""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form, 'post': post
        })
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    """View-функция для создания комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """View-функция для страницы с лентой постов избранных авторов"""
    context = {
        'page_obj': paginate(
            request,
            Post.objects.filter(author__following__user=request.user)
        )
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """View-функция для подписки на автора"""
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:follow_index')
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """View-функция для отписки от автора"""
    Follow.objects.filter(
        author=get_object_or_404(User, username=username),
        user=request.user
    ).delete()
    return redirect('posts:follow_index')
