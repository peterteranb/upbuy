import shutil
from io import StringIO
import tempfile

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings

from anuncios.models import Anuncio, FotoAnuncio

Usuario = get_user_model()
MEDIA_TEMPORAL = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class CargarDemoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)
        super().tearDownClass()

    def cargar(self, *args):
        call_command("cargar_demo", *args, stdout=StringIO())

    def test_es_idempotente(self):
        self.cargar()
        self.cargar()
        self.assertEqual(Usuario.objects.filter(email__startswith="demo").count(), 3)
        self.assertEqual(Anuncio.objects.filter(estado=Anuncio.Estado.ACTIVO).count(), 12)
        fotos = FotoAnuncio.objects.count()
        self.assertTrue(12 <= fotos <= 36)
        self.assertTrue(Usuario.objects.get(email="demo1@upb.edu").check_password("Demo12345"))
        self.assertTrue(Usuario.objects.get(email="demo2@upb.edu").email_verificado)

    def test_borrar_elimina_solo_datos_de_demo(self):
        otro = Usuario.objects.create_user(email="real@upb.edu", password="x")
        self.cargar()
        self.cargar("--borrar")
        self.assertFalse(Usuario.objects.filter(email__startswith="demo").exists())
        self.assertFalse(Anuncio.objects.exists())
        self.assertTrue(Usuario.objects.filter(pk=otro.pk).exists())
