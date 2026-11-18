from django.urls import path

from . import views

app_name = "anuncios"

urlpatterns = [
    path("publicar/", views.publicar, name="publicar"),
]
