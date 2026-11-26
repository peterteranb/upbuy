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


# Carreras de la UPB para el perfil. El campo del modelo sigue siendo texto libre.
CARRERAS = [
    "Administración de Empresas",
    "Arquitectura",
    "Comunicación Estratégica y Digital",
    "Derecho",
    "Diseño Gráfico y Producción Crossmedia",
    "Economía",
    "Ingeniería Civil",
    "Ingeniería Comercial",
    "Ingeniería de Sistemas Computacionales",
    "Ingeniería Electromecánica",
    "Ingeniería en Energía",
    "Ingeniería Financiera",
    "Ingeniería Industrial y de Sistemas",
    "Ingeniería Mecatrónica",
    "Medicina",
    "Odontología",
    "Otra",
]

TAMANO_MAXIMO_FOTO = 2 * 1024 * 1024  # 2 MB


class PerfilForm(BootstrapMixin, forms.ModelForm):
    carrera = forms.ChoiceField(label="Carrera", required=False)

    class Meta:
        model = Usuario
        fields = ["first_name", "last_name", "carrera", "foto"]
        labels = {"first_name": "Nombre", "last_name": "Apellido", "foto": "Foto de perfil"}
        widgets = {"foto": forms.FileInput(attrs={"accept": "image/*"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._aplicar_bootstrap()
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

        # Lista desplegable. Si el usuario escribió otra carrera al registrarse, se conserva.
        opciones = [("", "Elige tu carrera")] + [(c, c) for c in CARRERAS]
        actual = self.instance.carrera
        if actual and actual not in CARRERAS:
            opciones.append((actual, actual))
        self.fields["carrera"].choices = opciones
        self.fields["carrera"].widget.attrs["class"] = "form-select"

        # Se recuerda la foto anterior para borrarla si sube otra.
        self._foto_anterior = self.instance.foto.name if self.instance.foto else ""

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        # Solo se revisa el tamaño si subió un archivo nuevo.
        # Que sea imagen ya lo valida el ImageField del modelo.
        if "foto" in self.files and foto.size > TAMANO_MAXIMO_FOTO:
            raise forms.ValidationError("La foto no puede pesar más de 2 MB.")
        return foto

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit and self._foto_anterior and usuario.foto.name != self._foto_anterior:
            usuario.foto.storage.delete(self._foto_anterior)
        return usuario
