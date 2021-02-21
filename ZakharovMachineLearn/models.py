from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    rating = models.FloatField(default=0)
    views = models.IntegerField(default=0)
    estimation_amount = models.IntegerField(default=0)
    comment_amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class Estimation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, related_name="estimation_set", on_delete=models.CASCADE)
    score = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, on_delete=models.CASCADE)
    text = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)