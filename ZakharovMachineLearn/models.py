import os
import os.path
import uuid
import hashlib
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from django_resized import ResizedImageField


# путь и имя аватара по умолчанию для новых пользователей
DEFAULT_USER_AVATAR = os.path.join("avatars", "default-avatar.png")


def get_image_path(instance, filename):
    """
        формируем путь сохранения аватара, а также его имя
    """

    # получаем расширение файла
    filename_arr = filename.split(".")
    if filename_arr:
        ext = filename_arr[-1]
    else:
        ext = "jpg"

    # формируем имя файла как хэш от случайного значения и исходного имени файла
    m = hashlib.sha256()
    m.update((str(uuid.uuid1()) + filename).encode("utf-8"))

    filename = m.hexdigest() + f".{ext}"

    return os.path.join("avatars", filename) # возвращаем путь к аве вместе с каталогом


class User(AbstractUser):
    """
        Переопределенная модель пользователя, где мы добавляем свои поля:
        avatar - картинка аватара пользователя
        is_ad_shown - показывать ли для этого пользователя рекламу
    """
    avatar = ResizedImageField(
        size=[400, 400],  # преобразуем все картинки к такому размеру
        upload_to=get_image_path,  # куда загружать картинку
        default=DEFAULT_USER_AVATAR  # при создании пользователя испольузется картинка по умолчанию
    )
    is_ad_shown = models.BooleanField(default=True, null=False)

    def save(self, *args, **kwargs):
        """
            Переопределяем стандартное сохранение модели тем,
            что если пользователь не заполнил аватар, когда у него был загружен старый,
            то чтобы не становился дефолтным
        """
        if self.avatar == DEFAULT_USER_AVATAR:
            try:
                user = User.objects.get(pk=self.id)
                self.avatar = user.avatar
            except User.DoesNotExist:
                pass

        super().save(*args, **kwargs)


class PostCategory(models.Model):
    """
        Модель для категорий постов.
        Содержит название категории и дату создания.
    """
    title = models.CharField(max_length=300, help_text="Название категории")
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        """
           Функция для вывода объекта категории в виде строки.
           Если длина выше 50 символов, то берем первые 50 и добавляем многточие.
        """
        text = self.title[:50]
        if len(text) < len(self.title):
            text += "..."
        return text

    class Meta:
        # нужно для правильного отображения множественной формы названия в админке
        verbose_name_plural = "Post categories"


class Post(models.Model):
    """
        Модель поста
    """
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
        """
            Преобразование поста в строковую форму.
            При слишком длинном названии - берем 50 первых симовлов и
            добавляем многоточие
        """
        text = self.title[:50]
        if len(text) < len(self.title):
            text += "..."
        return text

    def save(self, *args, **kwargs):
        """
            Переопределяем сохранение модели так, что если обновилось название или тело поста,
            то нужно обвновить поле updated_at (дату обновления)
        """
        try:
            old_self = Post.objects.get(pk=self.id)
            if self.title != old_self.title or self.body != old_self.body:
                self.updated_at = datetime.now()
        except Post.DoesNotExist:
            pass
        super().save(*args, **kwargs)


class Estimation(models.Model):
    """
        Модель для оценки поста пользователем.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, related_name="estimation_set", on_delete=models.CASCADE)
    score = models.IntegerField(null=False)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.user} <{self.post}> - {self.score}"


class Comment(models.Model):
    """
        Модель комментариев к посту
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, default=None, on_delete=models.CASCADE)
    text = models.TextField(null=False)
    created_at = models.DateTimeField(default=datetime.now)

    def __str__(self):
        """
            Преобразование комментариев к строковому виду.
            При слишком большой длине ограничиваем и добавляем многоточие
        """
        text = self.text[:40]
        if len(text) != len(self.text):
            text += "..."
        return f"{self.user}: {text} [{self.post}]"
