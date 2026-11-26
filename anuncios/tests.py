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

class MisAnunciosTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()

        cls.vendedor = Usuario.objects.create_user(
            email="vendedor@example.com",
            password="PruebaTest2026!"
        )

        cls.otro_vendedor = Usuario.objects.create_user(
            email="otro@example.com",
            password="PruebaTest2026!"
        )

        cls.categoria, _ = Categoria.objects.get_or_create(
            slug="tecnologia",
            defaults={"nombre": "Tecnología"}
        )

    def setUp(self):
        self.url = reverse("anuncios:mis_anuncios")

    def crear_anuncio(
        self,
        titulo,
        estado,
        vendedor=None,
        motivo=""
    ):
        return Anuncio.objects.create(
            vendedor=vendedor or self.vendedor,
            categoria=self.categoria,
            titulo=titulo,
            descripcion="Producto de prueba",
            precio=150,
            estado_producto=Anuncio.EstadoProducto.USADO,
            punto_entrega=Anuncio.PuntoEntrega.CAMPUS,
            estado=estado,
            motivo_rechazo=motivo
        )

    def test_requiere_inicio_de_sesion(self):
        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(
            reverse("usuarios:login"),
            respuesta.url
        )

    def test_muestra_solo_anuncios_del_propietario(self):
        self.crear_anuncio(
            "Mi calculadora",
            Anuncio.Estado.EN_REVISION
        )

        self.crear_anuncio(
            "Anuncio de otro vendedor",
            Anuncio.Estado.RECHAZADO,
            vendedor=self.otro_vendedor,
            motivo="Motivo privado de otro vendedor"
        )

        self.client.force_login(self.vendedor)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Mi calculadora")
        self.assertNotContains(
            respuesta,
            "Anuncio de otro vendedor"
        )
        self.assertNotContains(
            respuesta,
            "Motivo privado de otro vendedor"
        )

    def test_muestra_los_cuatro_estados(self):
        for estado in Anuncio.Estado:
            self.crear_anuncio(
                f"Producto {estado.value}",
                estado
            )

        self.client.force_login(self.vendedor)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)

        for estado in Anuncio.Estado:
            self.assertContains(
                respuesta,
                estado.label
            )

        self.assertEqual(
            len(respuesta.context["anuncios"]),
            4
        )

    def test_muestra_motivo_de_rechazo(self):
        self.crear_anuncio(
            "Monitor",
            Anuncio.Estado.RECHAZADO,
            motivo="La fotografía no es clara."
        )

        self.client.force_login(self.vendedor)

        respuesta = self.client.get(self.url)

        self.assertContains(
            respuesta,
            "Motivo de rechazo:"
        )

        self.assertContains(
            respuesta,
            "La fotografía no es clara."
        )

    def test_no_muestra_motivo_en_anuncio_activo(self):
        self.crear_anuncio(
            "Teclado",
            Anuncio.Estado.ACTIVO,
            motivo="Motivo anterior de rechazo"
        )

        self.client.force_login(self.vendedor)

        respuesta = self.client.get(self.url)

        self.assertNotContains(
            respuesta,
            "Motivo anterior de rechazo"
        )

    def test_lista_vacia(self):
        self.client.force_login(self.vendedor)

        respuesta = self.client.get(self.url)

        self.assertEqual(respuesta.status_code, 200)

        self.assertContains(
            respuesta,
            "Todavía no tienes anuncios"
        )

    def test_orden_de_anuncios(self):
        antiguo = self.crear_anuncio(
            "Primer anuncio",
            Anuncio.Estado.ACTIVO
        )

        reciente = self.crear_anuncio(
            "Segundo anuncio",
            Anuncio.Estado.EN_REVISION
        )

        self.client.force_login(self.vendedor)

        respuesta = self.client.get(self.url)

        self.assertEqual(
            list(respuesta.context["anuncios"]),
            [reciente, antiguo]
        )
