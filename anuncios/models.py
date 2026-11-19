from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from decimal import Decimal


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Anuncio(models.Model):

    class Estado(models.TextChoices):
        EN_REVISION = "revision", "En revisión"
        ACTIVO = "activo", "Activo"
        RECHAZADO = "rechazado", "Rechazado"
        VENDIDO = "vendido", "Vendido"

    class EstadoProducto(models.TextChoices):
        NUEVO = "nuevo", "Nuevo"
        COMO_NUEVO = "como_nuevo", "Como nuevo"
        USADO = "usado", "Usado"

    class PuntoEntrega(models.TextChoices):
        CAMPUS = "campus", "Campus universitario"
        ENTRADA = "entrada", "Entrada principal"
        BIBLIOTECA = "biblioteca", "Biblioteca"
        A_CONVENIR = "convenir", "A convenir"

    vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="anuncios"
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="anuncios"
    )

    titulo = models.CharField(max_length=150)

    descripcion = models.TextField(blank=True)

    estado_producto = models.CharField(
        max_length=20,
        choices=EstadoProducto.choices
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ]
    )

    punto_entrega = models.CharField(
        max_length=20,
        choices=PuntoEntrega.choices
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.EN_REVISION
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Anuncio"
        verbose_name_plural = "Anuncios"
        constraints = [
            models.CheckConstraint(
                condition=Q(precio__gt=0),
                name="anuncio_precio_positivo"
            )
        ]

    def __str__(self):
        return self.titulo


class FotoAnuncio(models.Model):

    anuncio = models.ForeignKey(
        Anuncio,
        on_delete=models.CASCADE,
        related_name="fotos"
    )

    imagen = models.ImageField(
        upload_to="anuncios/"
    )

    def __str__(self):
        return f"Foto de {self.anuncio.titulo}"
