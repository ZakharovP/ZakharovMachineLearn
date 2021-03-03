import json

from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.views.generic.list import ListView
from django.db.models import Q

# импортируем формы
from .forms import (
    SignUpForm, SignInForm,
    CommentForm, PostSearchForm, UserForm, PasswordForm
)

# импортируем модели
from .models import (
    Post, Comment, Estimation
)

from . import settings


def mail_check(request):
    """
        Обработчик проверки функционирования отправки email на выбранные адрес
    """
    try:
        send_mail(
            'Тема сообщения',
            'Проверка',
            settings.EMAIL_HOST_USER,
            ["zakharovpetr@mail.ru"],
            fail_silently=False,
        )
    except Exception as err:
        print(err)
        return HttpResponse("Ошибка...")

    return HttpResponse("Отправлено!")


@require_http_methods(["GET"])
def main(request):
    """
        Представление главной страницы.
        Нынче не используется, так как теперь за обработку отвечает класс PostListView
    """
    posts = Post.objects.order_by("-created_at")

    search_form = PostSearchForm()

    context = {
       "posts": posts,
       "search_form": search_form
    }

    return render(request, "main.html", context, status=200)


class PostListView(ListView):
    """
        Представление-класс главной страницы.
    """
    template_name = "main.html"  # имя шаблона для страницы
    context_object_name = "posts"  # название списка вывода
    paginate_by = 4  # по сколько элементов на одной странице

    def get_queryset(self):
        """
            Функция получает QuerySet объектов для страницы
            - получение постов, соответствующих нужным параметрам
        """
        # параметр поиска поста по тексту
        q = self.request.GET.get("q", "")
        try:
            # получаем запрошенную категорию
            category = int(self.request.GET.get("category", ""))
        except ValueError:
            category = None

        # получаем посты с нужными параметрами
        # они должны быть активны и
        # заголовок или тело должно содержать искомый текст
        # и нужную категорию, если выбрана
        return Post.objects.order_by("-created_at").filter(
            Q(is_active=True) &
            (
                Q(body__icontains=q) |
                Q(title__icontains=q)
            ) &
            (Q(category_id=category) if category else Q())
        )

    def get_context_data(self, **kwargs):
        """
            Получение дополнительных параметров контекста.
            А именно - форма поиска.
        """
        context = super().get_context_data(**kwargs)
        context["search_form"] = PostSearchForm(self.request.GET)

        return context


@require_http_methods(["GET"])
def auth(request):
    """
        Обработчик возврата html страницы авторизации с двумя формами:
        - Входа
        - Регистрации
    """

    # если пользователь уже авторизован, то перенаправляем его на главную страницу
    if request.user.is_authenticated:
        return redirect("/")
    sign_up_form = SignUpForm()
    sign_in_form = SignInForm()
    context = {
        "sign_up_form": sign_up_form,
        "sign_in_form": sign_in_form
    }
    return render(request, "auth.html", context)


@require_http_methods(["POST"])
def  sign_in(request):
    """
        Обработчик POST запроса входа
    """
    # получаем две формы - регистрации и входа с переданными параметрами
    sign_up_form = SignUpForm()
    sign_in_form = SignInForm(data=request.POST)

    # если форма валидна
    if sign_in_form.is_valid():
        username = sign_in_form.cleaned_data.get('username')
        password = sign_in_form.cleaned_data.get('password')

        # получаем пользователя
        user = authenticate(username=username, password=password)
        login(request, user)  # авторизуем полученного пользователя
        return redirect('/')  # перенправляем на главную страницу
    else:
        # если форма не валидна, снова отсылаем шаблон авторизации
        context = {
            "sign_up_form": sign_up_form,
            "sign_in_form": sign_in_form
        }
        return render(request, "auth.html", context)


@require_http_methods(["POST"])
def sign_up(request):
    """
        Обработчик формы регистрации
    """
    # получаем форму регистрации с переданными парамтерами POST запроса
    # и пустую форму логина
    sign_up_form = SignUpForm(request.POST)
    sign_in_form = SignInForm()

    # если форма валидна
    if sign_up_form.is_valid():
        sign_up_form.save()
        username = sign_up_form.cleaned_data.get('username')
        password = sign_up_form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)  # аутентификация пользователя
        login(request, user)  # авторизация пользователя
        email = sign_up_form.cleaned_data["email"]  # получаем email пользователя

        # Если в настройках указано отправлять сообщение
        # на реальный email
        if settings.SEND_REAL_EMAIL:
            send_mail(
                'Уведомление о регистрации',
                'На данный email была совершена регистрация в приложении ZakharovMachineLearn',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

        return redirect('/')
    else:
        # если форма не валидна, снова отправляем шаблон авторизации
        context = {
            "sign_up_form": sign_up_form,
            "sign_in_form": sign_in_form
        }
        return render(request, "auth.html", context)


@require_http_methods(["GET"])
def post(request, post_id=-1):
    """
        Обработчик получения поста
    """

    # параметр, показывающий, что пост был прокомментирован
    comment_success = request.GET.get("comment_success")

    # пытаемся получить пост по его id
    try:
        post = Post.objects.get(pk=post_id)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        raise Http404("Страница не найдена")

    # увеличиваем кол-во просмотров на 1
    post.views += 1
    post.save()

    # получаем комментарии для данного поста
    comments = Comment.objects.filter(post_id=post_id).order_by("-created_at")

    # выбираем страницу комментариев
    comment_paginator = Paginator(comments, 2)
    page_number = request.GET.get("page", 1)
    comment_page = comment_paginator.page(page_number)

    # форма для комментариев
    comment_form = CommentForm()
    context = {
        "comment_form": comment_form,
        "post": post,
        "comments": comment_page.object_list,
        "comment_success": comment_success,
        "page_obj": comment_page
    }

    # если пользователь авторизован, то добавляем флаг, оценивал ли он уже этот пост
    if request.user.is_authenticated:
        context["is_user_estimated"] = len(post.estimation_set.filter(user=request.user)) > 0

    return render(request, "post.html", context)


@login_required
@require_http_methods(["POST"])
def comment(request, post_id=None):
    """
        Функция обработки добавления комментариев
    """
    if post_id is None:
        return redirect("/")
    form = CommentForm(request.POST)
    if form.is_valid():
        # если форма валидна, получаем комментарий,
        # прикрепляем к нему id поста и сохраняем
        instance = form.save(commit=False)
        instance.user = request.user
        instance.post_id = post_id
        instance.save()

        post = Post.objects.get(pk=post_id)
        # кол-во комментариев увеличиваем на 1
        post.comment_amount += 1
        post.save()

        return redirect(f"/post/{post_id}?comment_success=1")
    else:
        return redirect(f"/post/{post_id}?comment_success=0")


@login_required
@require_http_methods(["POST"])
def estimate(request):
    """
        Обработка оценок пользователем - сохранение их и
        изменение данных поста
    """
    try:
        data = json.loads(request.body)
        score = int(data.get("score", -1))
        post_id = data.get("post", -1)
    except ValueError:
        return JsonResponse({"success": False, "errors": ["Неправильный формат данных"]})

    # если оценка неправильная, дальше не идем
    if score <= 0 or post_id <= 0:
        return JsonResponse({ "success": False, "errors": ["Неправильный формат данных"] })

    # проверяем, оценивали ли мы уже этот пост
    estimation = Estimation.objects.filter(post_id=post_id, user=request.user)
    if estimation:
        # если оценивали - то выход
        return JsonResponse({ "success": False, "errors": ["Этот пост вы уже оценивали"] })

    estimation = Estimation(
        post_id=post_id,
        score=score,
        user=request.user
    )

    estimation.save()

    # пересчитываем рейтинг поста и его кол-во оценок
    post = Post.objects.get(pk=post_id)
    post.rating = (post.rating * post.estimation_amount + score) / (post.estimation_amount + 1)
    post.estimation_amount += 1

    post.save()

    return JsonResponse({
        "success": True,
        "rating": post.rating,
        "estimation_amount": post.estimation_amount
    })


@login_required
@require_http_methods(["GET", "POST"])
def account(request):
    """
        Обработчик аакаунта - как получение шаблона (GET запрос),
        так и обработка формы изменения данных (POST запрос)
    """
    context = {}
    if request.method == "GET":
        user_form = UserForm(
            instance=request.user,
            initial={
                'password': ''
            }
        )
    else:
        # проверяем на валидность присланные новые данные пользователя
        # проверяем как обычные данные из формы, так и файлы
        user_form = UserForm(request.POST, request.FILES)
        if user_form.is_valid():
            # если форма валидна, сохраняем данные
            instance = user_form.save(commit=False)
            instance.id = request.user.id
            instance.username = request.user.username
            fields = user_form.Meta.fields

            # нужно, чтобы не очищать пустым аватар
            if not user_form.cleaned_data["avatar"]:
                fields.remove("avatar")

            instance.save(update_fields=user_form.Meta.fields)
            return redirect("/account/")

    context["user_form"] = user_form
    return render(request, "account.html", context)

@login_required
@require_http_methods(["GET", "POST"])
def password(request):
    """
        Обработчик GET и POST запросов наизменение пароля
    """
    user = request.user
    context = {}

    if request.method == "GET":
        form = PasswordForm()
    else:
        form = PasswordForm(request.POST)
        form.user = user
        if form.is_valid():
            password = form.cleaned_data["password1"]
            user.set_password(password)
            user.save()

            # нужно обновить сессию, иначе будет автоматический logout
            update_session_auth_hash(request, user)

            return redirect("/account/")

    context["form"] = form
    return render(request, "password.html", context)


@login_required
def logout_view(request):
    """
        Обработка logout для юзера
    """
    logout(request)
    return redirect("/")