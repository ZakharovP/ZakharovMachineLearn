from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Comment, Estimation, PostCategory

UserAdmin.fieldsets += ('Custom fields set', {
    'fields': ('is_ad_shown',)
}),

admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Estimation)
admin.site.register(PostCategory)
