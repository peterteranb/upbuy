from django.contrib import admin

from .models import Anuncio, Categoria, FotoAnuncio


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}


class FotoAnuncioInline(admin.TabularInline):
    model = FotoAnuncio
    extra = 0


@admin.register(Anuncio)
class AnuncioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "vendedor", "categoria", "precio", "estado", "creado_en")
    list_filter = ("estado", "categoria")
    search_fields = ("titulo", "descripcion")
    inlines = [FotoAnuncioInline]
