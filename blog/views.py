from django.shortcuts import render, get_object_or_404
from blog.models import Comment, Post, Tag
from django.db.models import Count, Prefetch

TAG_PREFETCH_QS = Prefetch(
    'tags',
    queryset=Tag.objects.prefetch_tags()
    )


def serialize_post(post):
    tags = list(post.tags.all())
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', 0),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title if tags else None
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': getattr(tag, 'posts_with_tag_count', 0),
    }


def index(request):
    base_posts = Post.objects.all() \
                .select_related('author') \
                .prefetch_related(TAG_PREFETCH_QS)

    most_popular_posts = base_posts.popular().fetch_with_comments_count()
    most_fresh_posts = list(
        base_posts
        .annotate(comments_count=Count('comments', distinct=True))
        .order_by('-published_at')[:5]
    )

    most_popular_tags = (
        Tag.objects
        .annotate(posts_with_tag_count=Count('posts'))
        .order_by('-posts_with_tag_count')[:5]
    )

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags[:5]],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    post = get_object_or_404(Post.objects
                             .prefetch_related(TAG_PREFETCH_QS)
                             .select_related('author'),
                             slug=slug)
    comments = Comment.objects.filter(post=post).select_related('author')
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
        'likes_amount': Count(likes),
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
        .select_related('author') \
        .prefetch_related('tags') \
        .fetch_with_comments_count()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    related_posts = Post.objects.filter(tags__title=tag_title) \
                                .annotate(comments_count=Count(
                                    'comments',
                                    distinct=True
                                    )
                                ) \
                                .select_related('author') \
                                .prefetch_related(TAG_PREFETCH_QS)[:20]

    most_popular_tags = (
        Tag.objects
        .popular()
        .annotate(posts_with_tag_count=Count('posts'))
        .order_by('-posts_with_tag_count')[:5]
    )

    most_popular_posts = Post.objects.popular() \
        .select_related('author') \
        .prefetch_related('tags') \
        .fetch_with_comments_count()

    context = {
        'tag': tag_title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
