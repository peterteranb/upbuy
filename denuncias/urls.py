from django.urls import path

from . import views

app_name = "denuncias"

urlpatterns = [
    path("anuncio/<int:pk>/", views.crear, name="crear"),
]