from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

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
                anuncio.estado = Anuncio.Estado.ACTIVO
                anuncio.save()
                for orden, foto in enumerate(form.cleaned_data["fotos"]):
                    FotoAnuncio.objects.create(anuncio=anuncio, imagen=foto, orden=orden)
            messages.success(request, "Tu anuncio fue publicado.")
            return redirect("catalogo:detalle", pk=anuncio.pk)
    else:
        form = AnuncioForm()

    return render(request, "anuncios/publicar.html", {"form": form})
