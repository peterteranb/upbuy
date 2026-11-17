from django.shortcuts import render


# ---- lista: Raúl (UP-24) ----
def lista(request):
    # PROVISIONAL (UP-46): Raúl la reemplaza en UP-24.
    return render(request, "pendiente.html", {
        "titulo": "Catálogo",
        "responsable": "Raúl",
        "jira": "UP-24",
    })


# ---- detalle: Uriel (UP-25). Raúl no edita debajo de esta línea ----
def detalle(request, pk):
    # PROVISIONAL (UP-46): Uriel la reemplaza en UP-25.
    return render(request, "pendiente.html", {
        "titulo": f"Detalle del anuncio #{pk}",
        "responsable": "Uriel",
        "jira": "UP-25",
    })
