from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Comment, Estimation, PostCategory

# добавляем кастомные поля User в админке
UserAdmin.fieldsets += ('Дополнительные поля', {
    'fields': ('is_ad_shown', 'avatar')
}),

# регистрация моделей для отображения в админке
admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Estimation)
admin.site.register(PostCategory)
