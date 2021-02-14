from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)