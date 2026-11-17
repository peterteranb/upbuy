from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("registro/", views.registro, name="registro"),
    path("registro/enviado/", views.registro_enviado, name="registro_enviado"),
    path("verificar/<uidb64>/<token>/", views.verificar, name="verificar"),
    path("login/", auth_views.LoginView.as_view(template_name="usuarios/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
