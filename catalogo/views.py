from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from anuncios.models import Anuncio, Categoria


# ---- lista: Raúl (UP-24) ----
def lista(request):
    """Catálogo: anuncios activos, los más recientes primero (orden del Meta)."""
    anuncios = (
        Anuncio.objects.filter(estado=Anuncio.Estado.ACTIVO)
        .select_related("categoria", "vendedor")
        .prefetch_related("fotos")
    )

    categoria_actual = None
    slug = request.GET.get("categoria")
    if slug:
        categoria_actual = get_object_or_404(Categoria, slug=slug)
        anuncios = anuncios.filter(categoria=categoria_actual)

    page_obj = Paginator(anuncios, 12).get_page(request.GET.get("page"))

    return render(request, "catalogo/lista.html", {
        "page_obj": page_obj,
        "categorias": Categoria.objects.all(),
        "categoria_actual": categoria_actual,
    })


# ---- detalle: Uriel (UP-25). Raúl no edita debajo de esta línea ----
def detalle(request, pk):
    # PROVISIONAL (UP-46): Uriel la reemplaza en UP-25.
    return render(request, "pendiente.html", {
        "titulo": f"Detalle del anuncio #{pk}",
        "responsable": "Uriel",
        "jira": "UP-25",
    })
