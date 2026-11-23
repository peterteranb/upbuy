from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("registro/enviado/", views.registro_enviado, name="registro_enviado"),
    path("verificar/<uidb64>/<token>/", views.verificar, name="verificar"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="usuarios/login.html",
            authentication_form=LoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    # Django 5 solo acepta POST en LogoutView.
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
