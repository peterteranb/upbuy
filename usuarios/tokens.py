from django.contrib.auth.tokens import PasswordResetTokenGenerator


class VerificacionCorreoTokenGenerator(PasswordResetTokenGenerator):
    """Token del enlace de verificación de correo.

    El generador por defecto (pensado para restablecer contraseña) incluye
    last_login en el hash, así que iniciar sesión invalidaba el enlace. Como se
    permite iniciar sesión sin verificar, aquí no se usa last_login.
    """

    key_salt = "usuarios.tokens.VerificacionCorreoTokenGenerator"

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{timestamp}{user.email}"


token_verificacion = VerificacionCorreoTokenGenerator()
