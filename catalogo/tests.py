from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from anuncios.models import Anuncio, Categoria


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


class CatalogoListaTests(TestCase):
    """UP-24 · Catálogo por categorías, lo más reciente primero."""

    @classmethod
    def setUpTestData(cls):
        cls.vendedor = get_user_model().objects.create_user(
            email="vende@upb.edu", password="clave-segura-123"
        )
        cls.libros, _ = Categoria.objects.get_or_create(
            slug="test-libros", defaults={"nombre": "Test Libros"}
        )
        cls.tecno, _ = Categoria.objects.get_or_create(
            slug="test-tecno", defaults={"nombre": "Test Tecno"}
        )

    def crear_anuncio(self, titulo, categoria=None, estado=Anuncio.Estado.ACTIVO, hace_dias=0):
        anuncio = Anuncio.objects.create(
            vendedor=self.vendedor,
            categoria=categoria or self.libros,
            titulo=titulo,
            estado_producto=Anuncio.EstadoProducto.USADO,
            precio=Decimal("50.00"),
            punto_entrega=Anuncio.PuntoEntrega.BIBLIOTECA,
            estado=estado,
        )
        # creado_en es auto_now_add: se ajusta después para controlar el orden.
        Anuncio.objects.filter(pk=anuncio.pk).update(
            creado_en=timezone.now() - timedelta(days=hace_dias)
        )
        return anuncio

    def test_solo_aparecen_los_activos(self):
        activo = self.crear_anuncio("Cálculo de Stewart")
        for estado in (Anuncio.Estado.EN_REVISION, Anuncio.Estado.RECHAZADO, Anuncio.Estado.VENDIDO):
            self.crear_anuncio(f"Anuncio {estado}", estado=estado)
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertEqual(list(respuesta.context["page_obj"]), [activo])
        self.assertContains(respuesta, "Cálculo de Stewart")
        self.assertNotContains(respuesta, "Anuncio vendido")

    def test_el_mas_reciente_sale_primero(self):
        viejo = self.crear_anuncio("Viejo", hace_dias=5)
        nuevo = self.crear_anuncio("Nuevo", hace_dias=0)
        medio = self.crear_anuncio("Medio", hace_dias=2)
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertEqual(list(respuesta.context["page_obj"]), [nuevo, medio, viejo])

    def test_filtra_por_categoria(self):
        libro = self.crear_anuncio("Libro", categoria=self.libros)
        self.crear_anuncio("Laptop", categoria=self.tecno)
        respuesta = self.client.get(reverse("catalogo:lista"), {"categoria": self.libros.slug})
        self.assertEqual(list(respuesta.context["page_obj"]), [libro])
        self.assertEqual(respuesta.context["categoria_actual"], self.libros)
        self.assertNotContains(respuesta, "Laptop")

    def test_categoria_inexistente_da_404(self):
        respuesta = self.client.get(reverse("catalogo:lista"), {"categoria": "no-existe"})
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_anuncios_muestra_mensaje_vacio(self):
        respuesta = self.client.get(reverse("catalogo:lista"), {"categoria": self.tecno.slug})
        self.assertContains(respuesta, "Todavía no hay anuncios en Test Tecno.")

    def test_tarjeta_muestra_precio_punto_entrega_sin_foto_y_enlace(self):
        anuncio = self.crear_anuncio("Calculadora")
        respuesta = self.client.get(reverse("catalogo:lista"))
        self.assertContains(respuesta, "Bs 50,00")  # LANGUAGE_CODE es: coma decimal
        self.assertContains(respuesta, "Biblioteca")
        self.assertContains(respuesta, "Sin foto")
        self.assertContains(respuesta, reverse("catalogo:detalle", args=[anuncio.pk]))

    def test_pagina_de_12_y_conserva_categoria(self):
        for i in range(13):
            self.crear_anuncio(f"Libro {i}", hace_dias=i)
        respuesta = self.client.get(reverse("catalogo:lista"), {"categoria": self.libros.slug})
        self.assertEqual(len(respuesta.context["page_obj"]), 12)
        self.assertContains(respuesta, f"?categoria={self.libros.slug}&amp;page=2")
