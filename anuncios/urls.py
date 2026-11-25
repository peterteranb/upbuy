from django.urls import path

from . import views

app_name = "anuncios"

urlpatterns = [
    path("publicar/", views.publicar, name="publicar"),
    path("mios/", views.mis_anuncios, name="mis_anuncios"),
    path("<int:pk>/editar/", views.editar, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]