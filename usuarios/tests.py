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

    def test_enlace_sigue_valido_si_inicia_sesion_antes_de_verificar(self):
        # Se puede iniciar sesión sin verificar; eso no debe invalidar el enlace del correo.
        self.registrar()
        self.client.post(
            reverse("usuarios:login"), {"username": "ana.perez@upb.edu", "password": CLAVE}
        )
        self.client.get(self.enlace_del_correo())
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




# ---- UP-17 Perfil ----
import os
import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

from anuncios.models import Anuncio, Categoria

MEDIA_DE_PRUEBA = tempfile.mkdtemp()


def imagen_png(nombre="foto.png"):
    """Crea una imagen PNG pequeña en memoria para subirla en los tests."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "blue").save(buffer, format="PNG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/png")


def imagen_pesada():
    """PNG de ruido de 1000x1000: no se puede comprimir y pesa unos 3 MB."""
    buffer = BytesIO()
    Image.frombytes("RGB", (1000, 1000), os.urandom(1000 * 1000 * 3)).save(buffer, format="PNG")
    return SimpleUploadedFile("pesada.png", buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=MEDIA_DE_PRUEBA)
class PerfilTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_DE_PRUEBA, ignore_errors=True)

    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            email="ana@upb.edu", password="clave-segura-123", first_name="Ana", last_name="Pérez"
        )
        self.client.force_login(self.usuario)
        self.url = reverse("usuarios:perfil")

    def datos(self, **cambios):
        datos = {"first_name": "Ana", "last_name": "Pérez", "carrera": "Derecho"}
        datos.update(cambios)
        return datos

    def test_anonimo_va_al_login(self):
        self.client.logout()
        respuesta = self.client.get(self.url)
        self.assertRedirects(respuesta, f"{reverse('usuarios:login')}?next={self.url}")

    def test_muestra_el_correo_sin_poder_editarlo(self):
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, "ana@upb.edu")
        self.assertNotIn("email", respuesta.context["form"].fields)

    def test_editar_nombre_y_carrera(self):
        respuesta = self.client.post(self.url, self.datos(first_name="Ana María", carrera="Economía"))
        self.assertRedirects(respuesta, self.url)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.first_name, "Ana María")
        self.assertEqual(self.usuario.carrera, "Economía")

    def test_carrera_fuera_de_la_lista_se_rechaza(self):
        respuesta = self.client.post(self.url, self.datos(carrera="Carrera inventada"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["form"].has_error("carrera"))

    def test_subir_foto(self):
        respuesta = self.client.post(self.url, {**self.datos(), "foto": imagen_png()})
        self.assertRedirects(respuesta, self.url)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.foto.name.startswith("perfiles/"))

    def test_subir_otra_foto_borra_la_anterior(self):
        self.client.post(self.url, {**self.datos(), "foto": imagen_png("primera.png")})
        self.usuario.refresh_from_db()
        anterior = self.usuario.foto.name

        self.client.post(self.url, {**self.datos(), "foto": imagen_png("segunda.png")})
        self.usuario.refresh_from_db()
        self.assertNotEqual(self.usuario.foto.name, anterior)
        self.assertFalse(self.usuario.foto.storage.exists(anterior))

    def test_archivo_que_no_es_imagen_se_rechaza(self):
        texto = SimpleUploadedFile("notas.txt", b"esto no es una imagen", content_type="text/plain")
        respuesta = self.client.post(self.url, {**self.datos(), "foto": texto})
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.context["form"].has_error("foto"))
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.foto)

    def test_foto_de_mas_de_2_mb_se_rechaza(self):
        foto = imagen_pesada()
        self.assertGreater(foto.size, 2 * 1024 * 1024)
        respuesta = self.client.post(self.url, {**self.datos(), "foto": foto})
        self.assertContains(respuesta, "La foto no puede pesar más de 2 MB.")
        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.foto)


@override_settings(MEDIA_ROOT=MEDIA_DE_PRUEBA)
class TarjetaVendedorTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_DE_PRUEBA, ignore_errors=True)

    def setUp(self):
        self.vendedor = Usuario.objects.create_user(
            email="luis@upb.edu", password="clave-segura-123",
            first_name="Luis", last_name="Rojas", carrera="Derecho",
        )
        categoria, _ = Categoria.objects.get_or_create(slug="test-perfil", defaults={"nombre": "Test Perfil"})
        self.anuncio = Anuncio.objects.create(
            vendedor=self.vendedor,
            categoria=categoria,
            titulo="Libro de cálculo",
            estado_producto=Anuncio.EstadoProducto.USADO,
            precio=Decimal("50.00"),
            punto_entrega=Anuncio.PuntoEntrega.BIBLIOTECA,
            estado=Anuncio.Estado.ACTIVO,
        )
        self.url = reverse("catalogo:detalle", args=[self.anuncio.pk])

    def test_tarjeta_sin_foto_muestra_la_inicial(self):
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, "Luis Rojas")
        self.assertContains(respuesta, "Derecho")
        self.assertContains(respuesta, '<span class="rounded-circle')
        self.assertContains(respuesta, ">L</span>")

    def test_tarjeta_con_foto_muestra_la_foto(self):
        self.vendedor.foto = imagen_png()
        self.vendedor.save()
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, self.vendedor.foto.url)
        self.assertNotContains(respuesta, ">L</span>")
