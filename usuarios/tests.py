from django.contrib.auth import get_user_model
from django.test import TestCase

Usuario = get_user_model()


class EmailVerificadoTests(TestCase):
    def test_usuario_nuevo_no_esta_verificado(self):
        usuario = Usuario.objects.create_user(email="ana@upb.edu", password="clave-segura-123")
        self.assertFalse(usuario.email_verificado)

    def test_superusuario_nuevo_no_esta_verificado(self):
        admin = Usuario.objects.create_superuser(email="admin@upb.edu", password="clave-segura-123")
        self.assertFalse(admin.email_verificado)

    def test_se_puede_marcar_como_verificado(self):
        usuario = Usuario.objects.create_user(email="luis@upb.edu", password="clave-segura-123")
        usuario.email_verificado = True
        usuario.save(update_fields=["email_verificado"])
        usuario.refresh_from_db()
        self.assertTrue(usuario.email_verificado)


import re

from django.core import mail
from django.urls import reverse

from .forms import RegistroForm

CLAVE = "Mochila-Azul-2026"


def datos_registro(**cambios):
    datos = {
        "first_name": "Ana",
        "last_name": "Pérez",
        "email": "ana.perez@upb.edu",
        "carrera": "Ingeniería de Sistemas",
        "password1": CLAVE,
        "password2": CLAVE,
    }
    datos.update(cambios)
    return datos


class RegistroFormTests(TestCase):
    def test_rechaza_gmail(self):
        form = RegistroForm(data=datos_registro(email="ana@gmail.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("Usa tu correo institucional (@upb.edu).", form.errors["email"])

    def test_rechaza_upb_edu_bo(self):
        form = RegistroForm(data=datos_registro(email="ana@upb.edu.bo"))
        self.assertFalse(form.is_valid())
        self.assertIn("Usa tu correo institucional (@upb.edu).", form.errors["email"])

    def test_normaliza_correo(self):
        form = RegistroForm(data=datos_registro(email="  Ana.Perez@UPB.EDU "))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["email"], "ana.perez@upb.edu")

    def test_rechaza_contrasena_de_7_caracteres(self):
        form = RegistroForm(data=datos_registro(password1="Xq7#mPz", password2="Xq7#mPz"))
        self.assertFalse(form.is_valid())
        self.assertIn("password1", form.errors)

    def test_rechaza_contrasenas_distintas(self):
        form = RegistroForm(data=datos_registro(password2="Otra-Clave-2026"))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_rechaza_correo_duplicado(self):
        Usuario.objects.create_user(email="ana.perez@upb.edu", password=CLAVE)
        form = RegistroForm(data=datos_registro(email="ANA.PEREZ@upb.edu"))
        self.assertFalse(form.is_valid())
        self.assertIn("Ya existe una cuenta con este correo.", form.errors["email"])

    def test_nombre_y_apellido_obligatorios(self):
        form = RegistroForm(data=datos_registro(first_name="", last_name=""))
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)
        self.assertIn("last_name", form.errors)


class RegistroVistaTests(TestCase):
    def registrar(self):
        return self.client.post(reverse("usuarios:registro"), datos_registro())

    def enlace_del_correo(self):
        return re.search(r"https?://\S+", mail.outbox[0].body).group(0)

    def test_registro_valido_crea_usuario_no_verificado_y_envia_correo(self):
        respuesta = self.registrar()
        self.assertRedirects(respuesta, reverse("usuarios:registro_enviado"))
        usuario = Usuario.objects.get(email="ana.perez@upb.edu")
        self.assertFalse(usuario.email_verificado)
        self.assertEqual(usuario.first_name, "Ana")
        self.assertTrue(usuario.check_password(CLAVE))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Verifica tu cuenta de UPBuy")
        self.assertEqual(mail.outbox[0].to, ["ana.perez@upb.edu"])

    def test_registro_invalido_no_envia_correo(self):
        respuesta = self.client.post(reverse("usuarios:registro"), datos_registro(email="ana@gmail.com"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Usa tu correo institucional (@upb.edu).")
        self.assertEqual(len(mail.outbox), 0)
        self.assertFalse(Usuario.objects.exists())

    def test_enlace_del_correo_verifica(self):
        self.registrar()
        respuesta = self.client.get(self.enlace_del_correo(), follow=True)
        self.assertRedirects(respuesta, reverse("usuarios:login"))
        self.assertContains(respuesta, "Tu correo fue verificado. Ya puedes iniciar sesión.")
        self.assertTrue(Usuario.objects.get(email="ana.perez@upb.edu").email_verificado)

    def test_token_alterado_no_verifica(self):
        self.registrar()
        enlace = self.enlace_del_correo().rstrip("/")
        alterado = enlace[:-1] + ("a" if enlace[-1] != "a" else "b") + "/"
        respuesta = self.client.get(alterado)
        self.assertEqual(respuesta.status_code, 400)
        self.assertTemplateUsed(respuesta, "usuarios/verificacion_invalida.html")
        self.assertFalse(Usuario.objects.get(email="ana.perez@upb.edu").email_verificado)

    def test_uid_inexistente_no_verifica(self):
        respuesta = self.client.get(reverse("usuarios:verificar", args=["OTk5", "abc-123"]))
        self.assertTemplateUsed(respuesta, "usuarios/verificacion_invalida.html")

    def test_usuario_con_sesion_no_ve_registro(self):
        usuario = Usuario.objects.create_user(email="luis@upb.edu", password=CLAVE)
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse("usuarios:registro"))
        self.assertRedirects(respuesta, reverse("catalogo:lista"))


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(email="luis@upb.edu", password=CLAVE)

    def test_login_correcto_redirige_al_inicio(self):
        respuesta = self.client.post(
            reverse("usuarios:login"), {"username": "luis@upb.edu", "password": CLAVE}
        )
        self.assertRedirects(respuesta, "/")
        # La sesión se mantiene en la siguiente petición (equivale a recargar).
        respuesta = self.client.get("/")
        self.assertTrue(respuesta.wsgi_request.user.is_authenticated)

    def test_login_incorrecto_muestra_mensaje(self):
        respuesta = self.client.post(
            reverse("usuarios:login"), {"username": "luis@upb.edu", "password": "incorrecta"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Correo o contraseña incorrectos.")

    def test_login_muestra_enlace_a_registro(self):
        respuesta = self.client.get(reverse("usuarios:login"))
        self.assertContains(respuesta, "¿No tienes cuenta? Regístrate")
        self.assertContains(respuesta, "Correo institucional")

    def test_logout_por_post_redirige_al_login(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.post(reverse("usuarios:logout"))
        self.assertRedirects(respuesta, "/cuenta/login/")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_por_get_no_permitido(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get(reverse("usuarios:logout"))
        self.assertEqual(respuesta.status_code, 405)
