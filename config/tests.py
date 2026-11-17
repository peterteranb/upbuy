from django.test import TestCase
from django.urls import reverse


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
