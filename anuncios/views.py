from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import AnuncioForm
from .models import Anuncio, FotoAnuncio


@login_required
def publicar(request):
    if not request.user.email_verificado:
        messages.warning(request, "Verifica tu correo para poder publicar.")
        return redirect("catalogo:lista")

    if request.method == "POST":
        form = AnuncioForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                anuncio = form.save(commit=False)
                anuncio.vendedor = request.user
                anuncio.estado = Anuncio.Estado.EN_REVISION
                anuncio.save()
                for orden, foto in enumerate(form.cleaned_data["fotos"]):
                    FotoAnuncio.objects.create(anuncio=anuncio, imagen=foto, orden=orden)
            messages.success(request, "Tu anuncio fue enviado a revisión.")
            return redirect("anuncios:mis_anuncios")
    else:
        form = AnuncioForm()

    return render(request, "anuncios/publicar.html", {"form": form})



@login_required
def mis_anuncios(request):
    anuncios = (
        Anuncio.objects
        .filter(vendedor=request.user)
        .select_related("categoria")
        .prefetch_related("fotos")
        .order_by("-creado_en")
    )

    return render(
        request,
        "anuncios/mis_anuncios.html",
        {
            "anuncios": anuncios,
        }
    )



@login_required
def editar(request, pk):
    return render(request, "pendiente.html", {
        "titulo": f"Editar el anuncio #{pk}", "responsable": "Gonzalo", "jira": "UP-20",
    })


@login_required
@require_POST
def eliminar(request, pk):
    messages.info(request, "Eliminar anuncios todavía está en construcción (UP-20).")
    return redirect("anuncios:mis_anuncios")