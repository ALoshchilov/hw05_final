from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView
)
from django.urls import path, reverse_lazy

from . import views

app_name = 'users'

urlpatterns = [
    # Страница выхода из УЗ
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),

    # страница регистрации
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),

    # страница входа
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'password_reset/confirm/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_change_done')
        ),
        name='password_reset_confirm'
    ),
    # страница сброса пароля
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset_form'
    ),

    # страница смены пароля
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')
        ),
        name='password_change_form'
    ),
]
