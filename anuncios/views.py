from django.shortcuts import render


def publicar(request):
    # PROVISIONAL (UP-46): Gonzalo la reemplaza en UP-19.
    return render(request, "pendiente.html", {
        "titulo": "Publicar anuncio",
        "responsable": "Gonzalo",
        "jira": "UP-19",
    })
