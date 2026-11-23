"""Carga datos de demostración: 3 usuarios verificados y 12 anuncios activos con fotos.

Uso:
    python manage.py cargar_demo           # crea lo que falte (se puede correr varias veces)
    python manage.py cargar_demo --borrar  # elimina solo los datos de demo
"""
import textwrap
from datetime import timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from anuncios.models import Anuncio, Categoria, FotoAnuncio

Usuario = get_user_model()
P = Anuncio.PuntoEntrega
E = Anuncio.EstadoProducto

CLAVE_DEMO = "Demo12345"

USUARIOS = [
    {"email": "demo1@upb.edu", "first_name": "Ana", "last_name": "Quiroga",
     "carrera": "Ingeniería de Sistemas"},
    {"email": "demo2@upb.edu", "first_name": "Diego", "last_name": "Rojas",
     "carrera": "Administración de Empresas"},
    {"email": "demo3@upb.edu", "first_name": "Valeria", "last_name": "Mendoza",
     "carrera": "Ingeniería Industrial"},
]

# (vendedor, categoría, título, precio Bs, estado_producto, punto_entrega, horario, descripción, n.º fotos)
ANUNCIOS = [
    ("demo1@upb.edu", "Tecnología", "Calculadora Casio fx-991LA CW", "280", E.COMO_NUEVO, P.BIBLIOTECA,
     "Lunes a viernes, 12:00 a 14:00",
     "La usé un semestre para Cálculo II. Funciona perfecto, con tapa y manual.", 3),
    ("demo2@upb.edu", "Libros", "Cálculo de una variable – Stewart, 8.ª ed.", "150", E.USADO, P.BIBLIOTECA,
     "", "Tiene algunas notas con lápiz en los primeros capítulos. Sin hojas rotas.", 2),
    ("demo3@upb.edu", "Comida", "Salteñas de pollo por encargo (docena)", "84", E.NUEVO, P.ENTRADA,
     "Martes y jueves, 10:00 a 11:00",
     "Hechas en casa el mismo día. Haz tu pedido con un día de anticipación.", 1),
    ("demo1@upb.edu", "Ropa", "Polera oficial UPB talla M", "90", E.COMO_NUEVO, P.CAMPUS,
     "", "Polera azul con el logo bordado. Me quedó grande, la usé dos veces.", 2),
    ("demo2@upb.edu", "Postres", "Brownies caseros (caja de 6)", "30", E.NUEVO, P.CAMPUS,
     "Lunes a viernes, 15:00 a 17:00", "Con nueces y chispas de chocolate.", 1),
    ("demo3@upb.edu", "Libros", "Física Universitaria Sears-Zemansky Vol. 1", "180", E.USADO, P.A_CONVENIR,
     "", "Edición 14. Buen estado general, tapa un poco gastada.", 2),
    # Regla del negocio: no se permite vender tareas, trabajos ni tutorías.
    ("demo1@upb.edu", "Servicios", "Impresión y anillado de documentos", "15", E.NUEVO, P.BIBLIOTECA,
     "Lunes a viernes, 9:00 a 18:00",
     "Impresión a color y blanco y negro, anillado y empastado. Precio por anillado.", 1),
    ("demo2@upb.edu", "Tecnología", "Mouse inalámbrico Logitech M170", "75", E.USADO, P.ENTRADA,
     "", "Incluye el receptor USB. Pilas nuevas.", 2),
    ("demo3@upb.edu", "Entradas", "Entrada para la Noche de Talentos UPB", "50", E.NUEVO, P.CAMPUS,
     "", "Una entrada general. No puedo ir por un viaje.", 1),
    ("demo1@upb.edu", "Postres", "Torta de chocolate entera (12 porciones)", "120", E.NUEVO, P.A_CONVENIR,
     "Viernes, 16:00 a 18:00", "Por encargo, ideal para cumpleaños. Avisa con dos días.", 3),
    ("demo2@upb.edu", "Ropa", "Bata de laboratorio talla S", "70", E.COMO_NUEVO, P.CAMPUS,
     "", "Bata blanca manga larga, usada en un semestre de Química.", 1),
    ("demo3@upb.edu", "Otros", "Kit de dibujo técnico (escuadras y compás)", "60", E.USADO, P.ENTRADA,
     "Lunes a miércoles, 12:30 a 13:30", "Escuadras de 30 cm, compás metálico y transportador.", 2),
]

COLORES = [
    (31, 78, 140), (196, 69, 54), (46, 125, 50), (123, 31, 162),
    (230, 126, 34), (0, 121, 107), (84, 110, 122), (173, 20, 87),
]


def _fuente(tamano):
    """Fuente del sistema con tildes; la de Pillow por defecto no las tiene."""
    for nombre in ("arial.ttf", "DejaVuSans.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            continue
    return ImageFont.load_default(size=tamano)


def _imagen(titulo, color, numero):
    """JPEG de 800x600 de color sólido con el título escrito."""
    img = Image.new("RGB", (800, 600), color)
    dibujo = ImageDraw.Draw(img)
    fuente = _fuente(44)
    fuente_chica = _fuente(26)
    texto = "\n".join(textwrap.wrap(titulo, width=24))
    dibujo.multiline_text((400, 280), texto, font=fuente, fill="white", anchor="mm",
                          align="center", spacing=12)
    dibujo.text((400, 540), f"UPBuy · foto {numero}", font=fuente_chica,
                fill=(255, 255, 255), anchor="mm")
    salida = BytesIO()
    img.save(salida, format="JPEG", quality=85)
    return ContentFile(salida.getvalue())


class Command(BaseCommand):
    help = "Crea usuarios y anuncios de demostración (idempotente). Con --borrar los elimina."

    def add_arguments(self, parser):
        parser.add_argument("--borrar", action="store_true",
                            help="Elimina solo los usuarios de demo, sus anuncios y fotos.")

    def handle(self, *args, **opciones):
        if opciones["borrar"]:
            self.borrar()
        else:
            self.cargar()

    def borrar(self):
        correos = [u["email"] for u in USUARIOS]
        fotos = FotoAnuncio.objects.filter(anuncio__vendedor__email__in=correos)
        n_fotos = 0
        for foto in fotos:
            foto.imagen.delete(save=False)  # borra el archivo, no solo la fila
            n_fotos += 1
        n_anuncios = Anuncio.objects.filter(vendedor__email__in=correos).count()
        Usuario.objects.filter(email__in=correos).delete()  # CASCADE: anuncios y fotos
        self.stdout.write(self.style.SUCCESS(
            f"Datos de demo eliminados: {n_anuncios} anuncios, {n_fotos} fotos."
        ))

    @transaction.atomic
    def cargar(self):
        categorias = {c.nombre: c for c in Categoria.objects.all()}
        faltan = {a[1] for a in ANUNCIOS} - categorias.keys()
        if faltan:
            raise CommandError(f"Faltan categorías (¿corriste migrate?): {', '.join(sorted(faltan))}")

        usuarios = {}
        for datos in USUARIOS:
            usuario, _ = Usuario.objects.update_or_create(
                email=datos["email"],
                defaults={**datos, "email_verificado": True, "is_active": True},
            )
            if not usuario.check_password(CLAVE_DEMO):
                usuario.set_password(CLAVE_DEMO)
                usuario.save(update_fields=["password"])
            usuarios[datos["email"]] = usuario

        creados = 0
        ahora = timezone.now()
        for i, (correo, cat, titulo, precio, estado_p, punto, horario, desc, n_fotos) in enumerate(ANUNCIOS):
            anuncio, creado = Anuncio.objects.get_or_create(
                vendedor=usuarios[correo],
                titulo=titulo,
                defaults={
                    "categoria": categorias[cat],
                    "descripcion": desc,
                    "precio": Decimal(precio),
                    "estado_producto": estado_p,
                    "punto_entrega": punto,
                    "horario_entrega": horario,
                    "estado": Anuncio.Estado.ACTIVO,
                },
            )
            if creado:
                creados += 1
                # Fechas escalonadas en los últimos días para que el orden del catálogo sea realista.
                Anuncio.objects.filter(pk=anuncio.pk).update(creado_en=ahora - timedelta(hours=6 * (i + 1)))
            if not anuncio.fotos.exists():
                color = COLORES[i % len(COLORES)]
                for orden in range(n_fotos):
                    foto = FotoAnuncio(anuncio=anuncio, orden=orden)
                    foto.imagen.save(f"demo-{slugify(titulo)}-{orden + 1}.jpg",
                                     _imagen(titulo, color, orden + 1), save=False)
                    foto.save()

        self.stdout.write(self.style.SUCCESS(
            f"Demo lista: {len(usuarios)} usuarios (clave {CLAVE_DEMO}), "
            f"{creados} anuncios nuevos, {len(ANUNCIOS) - creados} ya existían."
        ))
