"""ZakharovMachineLearn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.views.generic.base import RedirectView

from . import settings

from .view import (
    PostListView, main, auth, sign_in,
    sign_up, logout_view,
    post, comment, estimate,
    mail_check, account, password
)

urlpatterns = [
    path('', PostListView.as_view()),
    path('favicon.ico/', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('admin/', admin.site.urls),
    path('auth/', auth),
    path('sign-in/', sign_in),
    path('sign-up/', sign_up),
    path('logout/', logout_view),
    path('post/', post),
    path('post/<int:post_id>/', post),
    path('estimate/', estimate),
    path('comment/<int:post_id>/', comment),
    path('mail_check/', mail_check),
    path('account/', account),
    path('password/', password)
]

# нужно чтобы можно было отображать загруженные пользователем файлы
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)