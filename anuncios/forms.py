from django import forms

from .models import Anuncio

MAX_FOTOS = 5
MAX_TAMANO_FOTO = 5 * 1024 * 1024  # 5 MB


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        limpiar = super().clean
        if isinstance(data, (list, tuple)):
            return [limpiar(archivo, initial) for archivo in data if archivo]
        archivo = limpiar(data, initial)
        return [archivo] if archivo else []


class AnuncioForm(forms.ModelForm):
    fotos = MultipleImageField(required=False, label="Fotos (1 a 5)")

    class Meta:
        model = Anuncio
        fields = [
            "titulo",
            "descripcion",
            "categoria",
            "precio",
            "estado_producto",
            "punto_entrega",
            "horario_entrega",
        ]
        labels = {
            "titulo": "Título",
            "descripcion": "Descripción",
            "categoria": "Categoría",
            "precio": "Precio",
            "estado_producto": "Estado del producto",
            "punto_entrega": "Punto de entrega",
            "horario_entrega": "Horario de entrega",
        }
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].empty_label = "Elige una categoría"
        self.fields["precio"].widget.attrs.update(
            {"min": "0.01", "step": "0.01", "inputmode": "decimal"}
        )
        self.fields["horario_entrega"].widget.attrs["placeholder"] = (
            self.fields["horario_entrega"].help_text
        )
        for campo in self.fields.values():
            clase = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"
            campo.widget.attrs["class"] = clase

    def full_clean(self):
        super().full_clean()
        for nombre in self.errors:
            if nombre in self.fields:
                self.fields[nombre].widget.attrs["class"] += " is-invalid"

    def clean_fotos(self):
        fotos = self.cleaned_data.get("fotos") or []
        if not 1 <= len(fotos) <= MAX_FOTOS:
            raise forms.ValidationError("Sube entre 1 y 5 fotos.")
        if any(foto.size > MAX_TAMANO_FOTO for foto in fotos):
            raise forms.ValidationError("Cada foto debe pesar 5 MB o menos.")
        return fotos
