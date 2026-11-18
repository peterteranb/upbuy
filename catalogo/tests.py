from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class PlantillaBaseTests(TestCase):
    """UP-24 · La barra de navegación cambia según haya sesión o no."""

    def test_sin_sesion_muestra_iniciar_sesion_y_crear_cuenta(self):
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertContains(respuesta, reverse("usuarios:login"))
        self.assertContains(respuesta, reverse("usuarios:registro"))
        self.assertNotContains(respuesta, reverse("anuncios:publicar"))
        self.assertNotContains(respuesta, "Cerrar sesión")

    def test_con_sesion_muestra_publicar_nombre_y_cerrar_sesion(self):
        usuario = get_user_model().objects.create_user(
            email="ana@upb.edu", password="clave-segura-123", first_name="Ana"
        )
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertContains(respuesta, reverse("anuncios:publicar"))
        self.assertContains(respuesta, "Ana")
        self.assertNotContains(respuesta, reverse("usuarios:registro"))

    def test_cerrar_sesion_es_un_formulario_post(self):
        usuario = get_user_model().objects.create_user(email="ana@upb.edu", password="clave-segura-123")
        self.client.force_login(usuario)
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertContains(
            respuesta, f'<form method="post" action="{reverse("usuarios:logout")}"', html=False
        )

    def test_mantiene_idioma_viewport_y_bootstrap(self):
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertContains(respuesta, '<html lang="es">')
        self.assertContains(respuesta, 'name="viewport"')
        self.assertContains(respuesta, "bootstrap@5.3.3/dist/css/bootstrap.min.css")
        self.assertContains(respuesta, "bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js")
        self.assertContains(respuesta, "css/upbuy.css")