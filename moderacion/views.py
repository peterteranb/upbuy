from django.shortcuts import render


# ---- Provisionales (UP-48). Uriel las reemplaza en UP-29 ----
def cola(request):
    return render(request, "pendiente.html", {
        "titulo": "Cola de moderación", "responsable": "Uriel", "jira": "UP-29",
    })


def revisar(request, pk):
    return render(request, "pendiente.html", {
        "titulo": f"Revisar el anuncio #{pk}", "responsable": "Uriel", "jira": "UP-29",
    })