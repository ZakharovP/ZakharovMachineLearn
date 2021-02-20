import json

from django.http import HttpResponse, JsonResponse, Http404
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import (
    NameForm, SignUpForm, SignInForm, CommentForm
)

from .models import (
    Post, Comment, Estimation
)


@login_required
@require_http_methods(["GET"])
def main(request):
    posts = Post.objects.all()

    context = {
        "posts": posts
    }

    return render(request, "main.html", context, status=200)

    """if request.method == "GET":
        context = {
            "name_form": NameForm()
        }
        return render(request, "main.html", context, status=200)
    elif request.method == "POST":
        form = NameForm(request.POST)
        if form.is_valid():
            your_name = form.cleaned_data["your_name"]
            return HttpResponse("your_name = " + your_name)

        print("NOT VALID!")

        context = {
            "name_form": form
        }

        return render(request, "main.html", context, status=200)
    response = HttpResponse("Method not allowed", 405)
    response.status_code = 405
    return response"""


@require_http_methods(["GET"])
def auth(request):
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
        return redirect('/')
    else:
        print("NOT VALID!", sign_up_form.errors)
        context = {
            "sign_up_form": sign_up_form,
            "sign_in_form": sign_in_form
        }
        return render(request, "auth.html", context)


@login_required
@require_http_methods(["GET"])
def post(request, post_id=-1):
    comment_success = request.GET.get("comment_success")

    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        raise Http404("Страница не найдена")

    post.views += 1
    post.save()

    comments = Comment.objects.filter(post_id=post_id)

    #print("post.estimations ======== ", post.estimation_set.filter(user=request.user))

    comment_form = CommentForm()
    print("comments = ", comments)
    context = {
        "comment_form": comment_form,
        "post": post,
        "comments": comments,
        "comment_success": comment_success,
        "is_user_estimated": len(post.estimation_set.filter(user=request.user)) > 0
    }
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