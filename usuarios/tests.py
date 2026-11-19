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
