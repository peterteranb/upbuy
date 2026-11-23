import shutil
import tempfile
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from anuncios.models import Anuncio, Categoria, FotoAnuncio

MEDIA_TEMPORAL = tempfile.mkdtemp()

# GIF de 1×1 píxel: basta para guardar un ImageField sin depender de archivos reales.
GIF_MINIMO = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00"
    b",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class CatalogoDetalleTests(TestCase):
    """UP-25 · Detalle del anuncio (HU-12)."""

    @classmethod
    def setUpTestData(cls):
        cls.vendedor = get_user_model().objects.create_user(
            email="maria@upb.edu",
            password="clave-segura-123",
            first_name="María",
            last_name="Quispe",
            carrera="Ingeniería de Sistemas",
        )
        cls.categoria, _ = Categoria.objects.get_or_create(
            slug="test-libros", defaults={"nombre": "Test Libros"}
        )
        cls.anuncio = Anuncio.objects.create(
            vendedor=cls.vendedor,
            categoria=cls.categoria,
            titulo="Cálculo de Stewart",
            descripcion="Séptima edición.\nCasi sin subrayar.",
            estado_producto=Anuncio.EstadoProducto.COMO_NUEVO,
            precio=Decimal("25.00"),
            punto_entrega=Anuncio.PuntoEntrega.BIBLIOTECA,
            horario_entrega="Lunes a viernes, 12:00 a 14:00",
            estado=Anuncio.Estado.ACTIVO,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def url(self, pk):
        return reverse("catalogo:detalle", args=[pk])

    def test_404_si_no_existe(self):
        respuesta = self.client.get(self.url(999999))
        self.assertEqual(respuesta.status_code, 404)

    def test_404_si_no_esta_activo(self):
        for estado in (Anuncio.Estado.EN_REVISION, Anuncio.Estado.RECHAZADO, Anuncio.Estado.VENDIDO):
            with self.subTest(estado=estado):
                Anuncio.objects.filter(pk=self.anuncio.pk).update(estado=estado)
                respuesta = self.client.get(self.url(self.anuncio.pk))
                self.assertEqual(respuesta.status_code, 404)

    def test_muestra_datos_del_anuncio_y_del_vendedor(self):
        respuesta = self.client.get(self.url(self.anuncio.pk))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "catalogo/detalle.html")
        self.assertContains(respuesta, "<title>Cálculo de Stewart · UPBuy</title>", html=False)
        self.assertContains(respuesta, "Cálculo de Stewart")
        self.assertContains(respuesta, "Bs 25,00")
        self.assertContains(respuesta, "Test Libros")
        self.assertContains(respuesta, "Como nuevo")
        self.assertContains(respuesta, "Biblioteca")
        self.assertContains(respuesta, "Lunes a viernes, 12:00 a 14:00")
        self.assertContains(respuesta, "Séptima edición.<br>Casi sin subrayar.", html=False)
        self.assertContains(respuesta, "María Quispe")
        self.assertContains(respuesta, "Ingeniería de Sistemas")
        self.assertContains(respuesta, reverse("catalogo:lista"))

    def test_no_muestra_el_correo_del_vendedor(self):
        respuesta = self.client.get(self.url(self.anuncio.pk))
        self.assertNotContains(respuesta, "maria@upb.edu")

    def test_vendedor_sin_nombre_muestra_usuario_upb(self):
        sin_nombre = get_user_model().objects.create_user(
            email="anonimo@upb.edu", password="clave-segura-123"
        )
        Anuncio.objects.filter(pk=self.anuncio.pk).update(vendedor=sin_nombre)
        respuesta = self.client.get(self.url(self.anuncio.pk))
        self.assertContains(respuesta, "Usuario UPB")
        self.assertNotContains(respuesta, "anonimo@upb.edu")

    def test_fotos_en_orden(self):
        # Se crean al revés para comprobar que manda el campo `orden`, no el id.
        segunda = FotoAnuncio.objects.create(
            anuncio=self.anuncio, orden=2,
            imagen=SimpleUploadedFile("segunda.gif", GIF_MINIMO, content_type="image/gif"),
        )
        primera = FotoAnuncio.objects.create(
            anuncio=self.anuncio, orden=1,
            imagen=SimpleUploadedFile("primera.gif", GIF_MINIMO, content_type="image/gif"),
        )
        respuesta = self.client.get(self.url(self.anuncio.pk))
        contenido = respuesta.content.decode()
        self.assertIn(primera.imagen.url, contenido)
        self.assertIn(segunda.imagen.url, contenido)
        self.assertLess(contenido.index(primera.imagen.url), contenido.index(segunda.imagen.url))
        self.assertContains(respuesta, "carousel-control-next")

    def test_una_sola_foto_sin_controles(self):
        FotoAnuncio.objects.create(
            anuncio=self.anuncio, orden=0,
            imagen=SimpleUploadedFile("unica.gif", GIF_MINIMO, content_type="image/gif"),
        )
        respuesta = self.client.get(self.url(self.anuncio.pk))
        self.assertContains(respuesta, "carousel-item active")
        self.assertNotContains(respuesta, "carousel-control-next")
