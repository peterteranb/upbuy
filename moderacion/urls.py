from django.urls import path

from . import views

app_name = "moderacion"

urlpatterns = [
    path("", views.cola, name="cola"),
    path("<int:pk>/", views.revisar, name="revisar"),
]