from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Comment, PostCategory

from django.core.exceptions import ValidationError


FIELD_TRANSLATION = {
    "username": "Ваш ник",
    "password": "Пароль",
    "password1": "Пароль",
    "password2": "Подтверждение пароля",
    "first_name": "Имя",
    "last_name": "Фамилия",
    "email": "Ваш E-mail"
}


class AuthMixin:
    def process_fields(self, fields):
        for fieldname in fields:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].label = ""
            placeholder = FIELD_TRANSLATION.get(fieldname, "")
            if fieldname.startswith("password"):
                self.fields[fieldname].widget = forms.PasswordInput(attrs={'placeholder': placeholder})
            else:
                self.fields[fieldname].widget = forms.TextInput(attrs={'placeholder': placeholder})


class SignUpForm(UserCreationForm, AuthMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.process_fields(fields=['username', 'password1', 'password2', 'first_name', 'last_name', 'email'])


    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)


class SignInForm(AuthenticationForm, AuthMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.process_fields(fields=['username', 'password'])

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError(
                "Аккаунт не активен!",
                code='inactive',
            )
        #if user.username.startswith('b'):
        #    raise ValidationError(
        #        _("Sorry, accounts starting with 'b' aren't welcome here."),
        #        code='no_b_users',
        #    )

    class Meta:
        model = User
        fields = ('username', 'password',)


class CommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Новое сообщение"}), label="")
    class Meta:
        model = Comment
        fields = ['text']


class PostSearchForm(forms.Form):
    q = forms.CharField(
        label='',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Поиск..."})
    )
    category = forms.ModelChoiceField(
        label='',
        queryset=PostCategory.objects.all(),
        widget=forms.Select(),
        required=False,
        empty_label=" --- Все категории"
    )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'avatar']


class PasswordForm(forms.Form):
    old_password = forms.CharField(label="", widget=forms.PasswordInput(attrs={"placeholder": "Старый пароль"}))
    password1 = forms.CharField(label="", widget=forms.PasswordInput(attrs={"placeholder": "Новый пароль"}))
    password2 = forms.CharField(label="", widget=forms.PasswordInput(attrs={"placeholder": "Подтверждение пароля"}))

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if hasattr(self, "user"):
            if not self.user.check_password(old_password):
                raise ValidationError('Неправильно введен старый пароль')

        if password1 != password2:
            raise ValidationError(
                "Пароли не совпадают"
            )
