import shutil
import tempfile
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
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

    def test_estado_por_defecto_es_activo(self):
        anuncio = self.crear_anuncio()
        self.assertEqual(anuncio.estado, Anuncio.Estado.ACTIVO)


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
