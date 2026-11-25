from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import resolve, reverse


class ContratoUrlsTests(TestCase):
    """Los nombres de URL de la sección 5.1 del plan deben existir siempre."""

    def test_reverse_de_todas_las_rutas(self):
        casos = [
            ("catalogo:lista", [], "/"),
            ("catalogo:detalle", [1], "/anuncio/1/"),
            ("anuncios:publicar", [], "/anuncios/publicar/"),
            ("usuarios:registro", [], "/cuenta/registro/"),
            ("usuarios:registro_enviado", [], "/cuenta/registro/enviado/"),
            ("usuarios:verificar", ["x", "y"], "/cuenta/verificar/x/y/"),
            ("usuarios:login", [], "/cuenta/login/"),
            ("usuarios:logout", [], "/cuenta/logout/"),
        ]
        for nombre, args, ruta in casos:
            with self.subTest(nombre=nombre):
                self.assertEqual(reverse(nombre, args=args), ruta)

    def test_inicio_responde_200(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)

    def test_login_responde_200(self):
        respuesta = self.client.get(reverse("usuarios:login"))
        self.assertEqual(respuesta.status_code, 200)


class ContratoUrlsSprint2Tests(TestCase):
    """UP-48 · Las URLs nuevas del contrato del Sprint 2 existen y resuelven."""

    def test_reverse_de_las_rutas_nuevas(self):
        casos = [
            ("anuncios:mis_anuncios", [], "/anuncios/mios/"),
            ("anuncios:editar", [1], "/anuncios/1/editar/"),
            ("anuncios:eliminar", [1], "/anuncios/1/eliminar/"),
            ("usuarios:perfil", [], "/cuenta/perfil/"),
            ("denuncias:crear", [1], "/denuncias/anuncio/1/"),
            ("moderacion:cola", [], "/moderacion/"),
            ("moderacion:revisar", [1], "/moderacion/1/"),
        ]
        for nombre, args, ruta in casos:
            with self.subTest(nombre=nombre):
                self.assertEqual(reverse(nombre, args=args), ruta)
                self.assertEqual(resolve(ruta).view_name, nombre)

    def test_barra_muestra_moderacion_solo_a_staff(self):
        Usuario = get_user_model()
        normal = Usuario.objects.create_user(email="normal@upb.edu", password="clave-segura-123")
        staff = Usuario.objects.create_user(email="staff@upb.edu", password="clave-segura-123", is_staff=True)

        self.client.force_login(normal)
        respuesta = self.client.get("/")
        self.assertContains(respuesta, reverse("anuncios:mis_anuncios"))
        self.assertContains(respuesta, reverse("usuarios:perfil"))
        self.assertNotContains(respuesta, reverse("moderacion:cola"))

        self.client.force_login(staff)
        self.assertContains(self.client.get("/"), reverse("moderacion:cola"))