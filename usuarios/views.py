from django.shortcuts import render

# PROVISIONAL (UP-46): Santiago reemplaza estas vistas en UP-14.
_PENDIENTE = {"responsable": "Santiago", "jira": "UP-14"}


def registro(request):
    return render(request, "pendiente.html", {"titulo": "Registro", **_PENDIENTE})


def registro_enviado(request):
    return render(request, "pendiente.html", {"titulo": "Registro enviado", **_PENDIENTE})


def verificar(request, uidb64, token):
    return render(request, "pendiente.html", {"titulo": "Verificar correo", **_PENDIENTE})
