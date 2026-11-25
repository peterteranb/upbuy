import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Anuncio, Categoria, FotoAnuncio

CATEGORIAS_INICIALES = [
    "Entradas", "Comida", "Postres", "Ropa",
    "Libros", "Tecnología", "Servicios", "Otros",
]


def imagen_png(nombre="foto.png"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color=(200, 50, 50)).save(buffer, format="PNG")
    return SimpleUploadedFile(nombre, buffer.getvalue(), content_type="image/png")


class AnuncioBaseTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.vendedor = get_user_model().objects.create_user(
            email="vendedor@example.com", password="clave-segura-123"
        )
        cls.categoria = Categoria.objects.get(nombre="Libros")

    def crear_anuncio(self, **kwargs):
        datos = {
            "vendedor": self.vendedor,
            "categoria": self.categoria,
            "titulo": "Libro de cálculo",
            "estado_producto": Anuncio.EstadoProducto.USADO,
            "precio": Decimal("50.00"),
            "punto_entrega": Anuncio.PuntoEntrega.BIBLIOTECA,
        }
        datos.update(kwargs)
        return Anuncio.objects.create(**datos)


class CategoriasInicialesTests(TestCase):

    def test_existen_las_ocho_categorias(self):
        nombres = set(Categoria.objects.values_list("nombre", flat=True))
        self.assertTrue(set(CATEGORIAS_INICIALES).issubset(nombres))
        self.assertEqual(
            Categoria.objects.filter(nombre__in=CATEGORIAS_INICIALES).count(), 8
        )
        self.assertTrue(Categoria.objects.filter(slug="tecnologia").exists())


class AnuncioTests(AnuncioBaseTestCase):

    def test_precio_cero_lanza_integrity_error(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.crear_anuncio(precio=Decimal("0"))

    def test_estado_por_defecto_es_en_revision(self):
        anuncio = self.crear_anuncio()
        self.assertEqual(anuncio.estado, Anuncio.Estado.EN_REVISION)


class FotoAnuncioTests(AnuncioBaseTestCase):

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)

    def test_fotos_ordenadas_por_orden(self):
        anuncio = self.crear_anuncio()
        foto_2 = FotoAnuncio.objects.create(anuncio=anuncio, imagen=imagen_png("b.png"), orden=2)
        foto_0 = FotoAnuncio.objects.create(anuncio=anuncio, imagen=imagen_png("c.png"), orden=0)
        foto_1 = FotoAnuncio.objects.create(anuncio=anuncio, imagen=imagen_png("a.png"), orden=1)

        self.assertEqual(list(anuncio.fotos.all()), [foto_0, foto_1, foto_2])


class PublicarAnuncioViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.verificado = Usuario.objects.create_user(
            email="verificado@example.com", password="clave-segura-123",
            email_verificado=True,
        )
        cls.sin_verificar = Usuario.objects.create_user(
            email="sinverificar@example.com", password="clave-segura-123",
        )
        cls.categoria = Categoria.objects.get(nombre="Libros")

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, ignore_errors=True)
        self.url = reverse("anuncios:publicar")

    def datos(self, fotos=1, **kwargs):
        datos = {
            "titulo": "Libro de cálculo",
            "descripcion": "Stewart, 7.ª edición",
            "categoria": self.categoria.pk,
            "precio": "50.00",
            "estado_producto": Anuncio.EstadoProducto.USADO,
            "punto_entrega": Anuncio.PuntoEntrega.BIBLIOTECA,
            "horario_entrega": "lunes a viernes, 12:00 a 14:00",
            "fotos": [imagen_png(f"foto{i}.png") for i in range(fotos)],
        }
        datos.update(kwargs)
        return datos

    def test_anonimo_redirige_al_login(self):
        respuesta = self.client.get(self.url)
        self.assertRedirects(
            respuesta, f"{reverse('usuarios:login')}?next={self.url}",
            fetch_redirect_response=False,
        )

    def test_usuario_sin_verificar_no_crea_anuncio(self):
        self.client.force_login(self.sin_verificar)
        respuesta = self.client.post(self.url, self.datos())
        self.assertRedirects(respuesta, reverse("catalogo:lista"), fetch_redirect_response=False)
        self.assertFalse(Anuncio.objects.exists())

    def test_get_muestra_formulario(self):
        self.client.force_login(self.verificado)
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "anuncios/publicar.html")
        self.assertContains(respuesta, 'enctype="multipart/form-data"')

    def test_precio_cero_da_error(self):
        self.client.force_login(self.verificado)
        respuesta = self.client.post(self.url, self.datos(precio="0"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("precio", respuesta.context["form"].errors)
        self.assertFalse(Anuncio.objects.exists())

    def test_sin_fotos_da_error(self):
        self.client.force_login(self.verificado)
        respuesta = self.client.post(self.url, self.datos(fotos=0))
        self.assertFormError(respuesta.context["form"], "fotos", "Sube entre 1 y 5 fotos.")
        self.assertFalse(Anuncio.objects.exists())

    def test_seis_fotos_da_error(self):
        self.client.force_login(self.verificado)
        respuesta = self.client.post(self.url, self.datos(fotos=6))
        self.assertFormError(respuesta.context["form"], "fotos", "Sube entre 1 y 5 fotos.")
        self.assertFalse(Anuncio.objects.exists())

    def test_publicacion_valida(self):
        self.client.force_login(self.verificado)
        respuesta = self.client.post(self.url, self.datos(fotos=3))

        self.assertEqual(Anuncio.objects.count(), 1)
        anuncio = Anuncio.objects.get()
        self.assertEqual(anuncio.estado, Anuncio.Estado.EN_REVISION)
        self.assertEqual(anuncio.vendedor, self.verificado)
        self.assertEqual(anuncio.precio, Decimal("50.00"))
        fotos = list(anuncio.fotos.all())
        self.assertEqual([f.orden for f in fotos], [0, 1, 2])
        self.assertEqual(
            [f.imagen.name.rsplit("/", 1)[-1][:5] for f in fotos],
            ["foto0", "foto1", "foto2"],
        )
        self.assertRedirects(respuesta, reverse("anuncios:mis_anuncios"), fetch_redirect_response=False)
        mensajes = [str(m) for m in respuesta.wsgi_request._messages]
        self.assertIn("Tu anuncio fue enviado a revisión.", mensajes)