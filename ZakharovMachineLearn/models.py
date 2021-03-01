import os
import os.path
import uuid
import hashlib
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from PIL import Image
from django_resized import ResizedImageField


DEFAULT_USER_AVATAR = os.path.join("avatars", "default-avatar.png")


def get_image_path(instance, filename):
    print("get_image_path instance = ", instance)
    print("get_image_path FILENAME = ", filename)
    print("__package__ = ", __package__)

    filename_arr = filename.split(".")
    if filename_arr:
        ext = filename_arr[-1]
    else:
        ext = "jpg"

    print("FILENAME ==== ", filename)
    print("EXT = ", ext)

    m = hashlib.sha256()
    m.update((str(uuid.uuid1()) + filename).encode("utf-8"))

    filename = m.hexdigest() + f".{ext}"

    return os.path.join("avatars", filename)


class User(AbstractUser):
    avatar = ResizedImageField(
        size=[400, 400],
        upload_to=get_image_path,
        default=DEFAULT_USER_AVATAR
    )
    is_ad_shown = models.BooleanField(default=True, null=False)

    def save(self, *args, **kwargs):
        if self.avatar == DEFAULT_USER_AVATAR:
            user = User.objects.get(pk=self.id)
            self.avatar = user.avatar

        super().save(*args, **kwargs)


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
