from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import (
    NameForm, SignUpForm, SignInForm, CommentForm
)


@login_required
@require_http_methods(["GET"])
def main(request):
    if request.method == "GET":
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
    return response


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
    comment_form = CommentForm()
    context = {
        "comment_form": comment_form,
        "post_id": post_id
    }
    return render(request, "post.html", context)


@login_required
@require_http_methods(["POST"])
def comment(request, post_id=-1):
    form = CommentForm(request.POST)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        return HttpResponse("Ваше сообщение сохранено!")
    else:
        return HttpResponse("Что-то пошло не так...")
    #return render(request, "post.html", context)


@login_required
def logout_view(request):
    logout(request)
    return redirect("/")