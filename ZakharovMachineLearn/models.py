from datetime import datetime

from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200, help_text="Заголовок поста")
    body = models.TextField(help_text="Тело поста")
    rating = models.FloatField(default=0, help_text="Рейтинг поста")
    views = models.IntegerField(default=0, help_text="Количество просмотров")
    estimation_amount = models.IntegerField(default=0, help_text="Количество оценок")
    comment_amount = models.IntegerField(default=0, help_text="Количество комментариев")
    is_active = models.BooleanField(default=True, null=False, help_text="Включен ли в выдачу")
    updated_at = models.DateTimeField(default=datetime.now, help_text="Дата обновления контента")
    created_at = models.DateTimeField(default=datetime.now, help_text="Дата создания")

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


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, on_delete=models.CASCADE)
    text = models.TextField(null=False)
    created_at = models.DateTimeField(default=datetime.now)