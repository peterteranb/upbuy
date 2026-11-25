"""URLs principales de UPBuy.

Los nombres de las rutas son un contrato del equipo (docs/sprint-1/PLAN-SPRINT-1.md, sección 5.1).
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("catalogo.urls")),
    path("cuenta/", include("usuarios.urls")),
    path("anuncios/", include("anuncios.urls")),
    path("moderacion/", include("moderacion.urls")),
    path("denuncias/", include("denuncias.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)