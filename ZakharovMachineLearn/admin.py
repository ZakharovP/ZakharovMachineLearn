from django.contrib import admin

from .models import Post, Comment, Estimation, PostCategory


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Estimation)
admin.site.register(PostCategory)