from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import RegistroForm
from .tokens import token_verificacion

Usuario = get_user_model()


def _enviar_correo_verificacion(request, usuario):
    uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
    token = token_verificacion.make_token(usuario)
    enlace = request.build_absolute_uri(
        reverse("usuarios:verificar", kwargs={"uidb64": uidb64, "token": token})
    )
    cuerpo = render_to_string(
        "usuarios/correo_verificacion.txt", {"usuario": usuario, "enlace": enlace}
    )
    send_mail("Verifica tu cuenta de UPBuy", cuerpo, None, [usuario.email])


def registro(request):
    if request.user.is_authenticated:
        return redirect("catalogo:lista")

    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            _enviar_correo_verificacion(request, usuario)
            return redirect("usuarios:registro_enviado")
    else:
        form = RegistroForm()
    return render(request, "usuarios/registro.html", {"form": form})


def registro_enviado(request):
    return render(request, "usuarios/registro_enviado.html")


def verificar(request, uidb64, token):
    try:
        pk = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=pk)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario is not None and token_verificacion.check_token(usuario, token):
        if not usuario.email_verificado:
            usuario.email_verificado = True
            usuario.save(update_fields=["email_verificado"])
        messages.success(request, "Tu correo fue verificado. Ya puedes iniciar sesión.")
        return redirect("usuarios:login")

    return render(request, "usuarios/verificacion_invalida.html", status=400)


# ---- Provisional (UP-48). Santiago la reemplaza en UP-17 ----
@login_required
def perfil(request):
    return render(request, "pendiente.html", {
        "titulo": "Mi perfil", "responsable": "Santiago", "jira": "UP-17",
    })