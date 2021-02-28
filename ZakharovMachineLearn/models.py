from datetime import datetime

from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_ad_shown = models.BooleanField(default=True, null=False)

class PostCategory(models.Model):
    title = models.CharField(max_length=300, help_text="Название категории")
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        text = self.title[:50]
        if len(text) < len(self.title):
            text += "..."
        return text

    class Meta:
        verbose_name_plural = "Post categories"


class Post(models.Model):
    title = models.CharField(max_length=200, help_text="Заголовок поста")
    body = models.TextField(help_text="Тело поста")
    rating = models.FloatField(default=0, help_text="Рейтинг поста")
    views = models.IntegerField(default=0, help_text="Количество просмотров")
    estimation_amount = models.IntegerField(default=0, help_text="Количество оценок")
    comment_amount = models.IntegerField(default=0, help_text="Количество комментариев")
    is_markdown = models.BooleanField(default=False, null=False, blank=True)
    is_active = models.BooleanField(default=True, null=False, help_text="Включен ли в выдачу")
    category = models.ForeignKey(PostCategory, null=True, blank=True, default=None, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(default=datetime.now, help_text="Дата обновления контента")
    created_at = models.DateTimeField(default=datetime.now, help_text="Дата создания")

    def __str__(self):
        text = self.title[:50]
        if len(text) < len(self.title):
            text += "..."
        return text

    def save(self, *args, **kwargs):
        try:
            old_self = Post.objects.get(pk=self.id)
            if self.title != old_self.title or self.body != old_self.body:
                self.updated_at = datetime.now()
        except Post.DoesNotExist:
            pass
        super().save(*args, **kwargs)


class Estimation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, related_name="estimation_set", on_delete=models.CASCADE)
    score = models.IntegerField(null=False)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.user} <{self.post}> - {self.score}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, on_delete=models.CASCADE)
    text = models.TextField(null=False)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        text = self.text[:40]
        if len(text) != len(self.text):
            text += "..."
        return f"{self.user}: {text} [{self.post}]"
