import json

from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.views.generic.list import ListView



from .forms import (
    NameForm, SignUpForm, SignInForm, CommentForm
)

from .models import (
    Post, Comment, Estimation
)

from . import settings

def mail_check(request):
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
   posts = Post.objects.order_by("-created_at")

   context = {
       "posts": posts
   }

   return render(request, "main.html", context, status=200)


class PostListView(ListView):
    template_name = "main.html"
    context_object_name = "posts"
    paginate_by = 4

    def get_queryset(self):
        return Post.objects.order_by("-created_at").filter(is_active=True)


@require_http_methods(["GET"])
def auth(request):
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
    sign_up_form = SignUpForm()
    sign_in_form = SignInForm(data=request.POST)
    if sign_in_form.is_valid():
        print("VALID!!!")
        username = sign_in_form.cleaned_data.get('username')
        password = sign_in_form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('/')
    else:
        print("NOT VALID!!!", sign_in_form.errors)
        context = {
            "sign_up_form": sign_up_form,
            "sign_in_form": sign_in_form
        }
        return render(request, "auth.html", context)


    return HttpResponse("sign_in")


@require_http_methods(["POST"])
def sign_up(request):
    sign_up_form = SignUpForm(request.POST)
    sign_in_form = SignInForm()
    if sign_up_form.is_valid():
        print("VALID!")
        sign_up_form.save()
        username = sign_up_form.cleaned_data.get('username')
        password = sign_up_form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)


        email = sign_up_form.cleaned_data["email"]
        print("email = ", email)

        send_mail(
            'Уведомление о регистрации',
            'На данный email была совершена регистрация в приложении ZakharovMachineLearn',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        return redirect('/')
    else:
        print("NOT VALID!", sign_up_form.errors)
        context = {
            "sign_up_form": sign_up_form,
            "sign_in_form": sign_in_form
        }
        return render(request, "auth.html", context)


@require_http_methods(["GET"])
def post(request, post_id=-1):
    comment_success = request.GET.get("comment_success")

    try:
        post = Post.objects.get(pk=post_id)
        if not post.is_active:
            raise Post.DoesNotExist()
    except Post.DoesNotExist:
        raise Http404("Страница не найдена")

    post.views += 1
    post.save()

    comments = Comment.objects.filter(post_id=post_id).order_by("-created_at")
    comment_paginator = Paginator(comments, 2)

    page_number = request.GET.get("page", 1)
    comment_page = comment_paginator.page(page_number)

    comment_form = CommentForm()
    context = {
        "comment_form": comment_form,
        "post": post,
        "comments": comment_page.object_list,
        "comment_success": comment_success,
        "page_obj": comment_page
    }

    if request.user.is_authenticated:
        context["is_user_estimated"] = len(post.estimation_set.filter(user=request.user)) > 0

    return render(request, "post.html", context)


@login_required
@require_http_methods(["POST"])
def comment(request, post_id=None):
    if post_id is None:
        return redirect("/")
    form = CommentForm(request.POST)
    if form.is_valid():
        print("cleaned_data = ", form.cleaned_data)
        print("post_id comment", post_id)
        instance = form.save(commit=False)
        instance.user = request.user
        instance.post_id = post_id
        instance.save()

        post = Post.objects.get(pk=post_id)
        post.comment_amount += 1
        post.save()

        return redirect(f"/post/{post_id}?comment_success=1")
    else:
        print(form.errors)
        return redirect(f"/post/{post_id}?comment_success=0")
    #return render(request, "post.html", context)


@login_required
@require_http_methods(["POST"])
def estimate(request):
    try:
        data = json.loads(request.body)
        score = int(data.get("score", -1))
        post_id = data.get("post", -1)
    except ValueError:
        return JsonResponse({"success": False, "errors": ["Неправильный формат данных"]})

    if score <= 0 or post_id <= 0:
        return JsonResponse({ "success": False, "errors": ["Неправильный формат данных"] })

    estimation = Estimation.objects.filter(post_id=post_id, user=request.user)
    if estimation:
        return JsonResponse({ "success": False, "errors": ["Этот пост вы уже оценивали"] })

    print("DATA = ", data)
    estimation = Estimation(
        post_id=post_id,
        score=score,
        user=request.user
    )

    estimation.save()

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
def logout_view(request):
    logout(request)
    return redirect("/")