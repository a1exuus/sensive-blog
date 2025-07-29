from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    raw_id_fields = ('likes', 'tags', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    raw_id_fields = ('posts',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ('post', 'author')
    list_display = ['author', 'text', 'post', 'published_at']
