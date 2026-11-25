from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# ---- Provisional (UP-48). Santiago la reemplaza en UP-33 ----
@login_required
def crear(request, pk):
    return render(request, "pendiente.html", {
        "titulo": f"Denunciar el anuncio #{pk}", "responsable": "Santiago", "jira": "UP-33",
    })