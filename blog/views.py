from django.shortcuts import render
from blog.models import Comment, Post, Tag
from django.db.models import Count

def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', 0),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.annotate(posts_with_tag_count=Count('posts'))],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_with_tag_count,
    }


def index(request):
    most_popular_posts = Post.objects.popular() \
                        .fetch_with_comments_count() \
                        .select_related('author') \
                        .prefetch_related('tags')

    fresh_posts = Post.objects.annotate(
        comments_count=Count('comments', distinct=True)
        ).order_by('published_at') \
         .prefetch_related('tags') \
         .select_related('author')
    most_fresh_posts = list(fresh_posts)[-5:]

    most_popular_tags = (
        Tag.objects
            .popular()
            .annotate(posts_with_tag_count=Count('posts'))
            .order_by('-posts_with_tag_count')[:5]
    )


    context = {
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post_optimized(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def get_likes_count(post):
    return Count(post.likes)


def post_detail(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comment.objects.filter(post=post)
    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    likes = post.likes.all()

    related_tags = post.tags.all()

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': len(likes),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = (
        Tag.objects
        .popular()
        .annotate(posts_with_tag_count=Count('posts'))
        .order_by('-posts_with_tag_count')[:5]
    )


    most_popular_posts = Post.objects.popular() \
                        .prefetch_related('author') \
                        .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    related_posts = (
        Post.objects
            .filter(tags__title=tag_title)
            .annotate(comments_count=Count('comments', distinct=True))
            .prefetch_related('author')
    )[:20]
    most_popular_tags = (
        Tag.objects
        .popular()
        .annotate(posts_with_tag_count=Count('posts'))
        .order_by('-posts_with_tag_count')[:5]
    )


    most_popular_posts = Post.objects.popular() \
                        .prefetch_related('author') \
                        .fetch_with_comments_count()

    context = {
        'tag': tag_title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
