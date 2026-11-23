from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

Usuario = get_user_model()


class BootstrapMixin:
    """Aplica las clases de Bootstrap y marca con is-invalid los campos con error."""

    def _aplicar_bootstrap(self):
        for campo in self.fields.values():
            campo.widget.attrs["class"] = "form-control"

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                self.fields[nombre].widget.attrs["class"] += " is-invalid"


class RegistroForm(BootstrapMixin, forms.Form):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="Correo institucional", max_length=254)
    carrera = forms.CharField(label="Carrera", max_length=80, required=False)
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Al menos 8 caracteres.",
    )
    password2 = forms.CharField(
        label="Repite la contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aplicar_bootstrap()
        self.fields["email"].widget.attrs.update(
            {"placeholder": f"tu.nombre{settings.UPBUY_DOMINIO_CORREO}", "autocomplete": "email"}
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email.endswith(settings.UPBUY_DOMINIO_CORREO):
            raise forms.ValidationError(
                f"Usa tu correo institucional ({settings.UPBUY_DOMINIO_CORREO})."
            )
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        elif password1:
            usuario = Usuario(
                email=cleaned.get("email", ""),
                first_name=cleaned.get("first_name", ""),
                last_name=cleaned.get("last_name", ""),
            )
            try:
                validate_password(password1, usuario)
            except forms.ValidationError as error:
                self.add_error("password1", error)
        return cleaned

    def save(self):
        datos = self.cleaned_data
        return Usuario.objects.create_user(
            email=datos["email"],
            password=datos["password1"],
            first_name=datos["first_name"].strip(),
            last_name=datos["last_name"].strip(),
            carrera=datos.get("carrera", "").strip(),
            email_verificado=False,
        )


class LoginForm(BootstrapMixin, AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Correo o contraseña incorrectos.",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self._aplicar_bootstrap()
        self.fields["username"].label = "Correo institucional"
        self.fields["username"].widget.attrs["autocomplete"] = "email"
        self.fields["password"].label = "Contraseña"

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()
