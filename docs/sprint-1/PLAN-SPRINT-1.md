# UPBuy · Sprint 1: qué hace cada uno

> **Sprint 1:** jueves 13 → **viernes 20 de noviembre de 2026, 12:00** (fechas de Jira). Documento armado el martes 17.
> **Objetivo del Sprint:** un estudiante UPB puede registrarse, publicar un anuncio y verlo en el catálogo.
> **Jira:** https://urieltb2402.atlassian.net (proyecto `UP`) · **GitHub:** https://github.com/peterteranb/upbuy
> **Carpeta local recomendada:** `C:\proyectos\upbuy`

| Rol | Persona |
|---|---|
| Product Owner | Raúl Vaca |
| Scrum Master | Uriel Terán (con apoyo de Claude) |
| Developers | Uriel Terán, Santiago Arauz, Gonzalo Cardenas, Raúl Vaca |

## Sprint Backlog

| Jira | Historia | Pts | Responsable | Rama(s) | PR listo |
|---|---|---|---|---|---|
| UP-46 | Fundación técnica (configuración base) | — | Uriel | `UP-46-fundacion` | **mar 17, 17:00** |
| UP-14 | HU-01 Registrarme con correo institucional | 5 | Santiago | `UP-14-email-verificado`, luego `UP-14-registro-login` | migración: **mié 18, 12:00** · resto: **jue 19, 12:00** |
| UP-15 | HU-02 Iniciar y cerrar sesión | 3 | Santiago | `UP-14-registro-login` (misma rama) | jue 19, 12:00 |
| UP-19 | HU-06 Publicar un anuncio | 8 | Gonzalo | `UP-19-modelos`, luego `UP-19-publicar-anuncio` | modelos: **mié 18, 12:00** · publicar: **jue 19, 12:00** |
| UP-24 | HU-11 Catálogo por categorías y recientes | 5 | Raúl | `UP-24-plantilla-base`, luego `UP-24-catalogo` | plantilla: mié 18, 12:00 · catálogo: jue 19, 12:00 |
| UP-25 | HU-12 Detalle del anuncio y del vendedor | 3 | Uriel | `UP-25-detalle` | jue 19, 12:00 (si se atrasa, vuelve al backlog) |

Total: 24 puntos. **El sprint no se alarga.** Si algo no llega, se recorta el alcance (primero HU-12).

---

# PARTE 1 · Resumen simple

**Uriel**
- **Hoy:** integro la rama de Santiago a `main` y subo la "fundación": configuración, apps vacías, URLs, plantilla base provisional y README.
- **Miércoles:** detalle del anuncio (HU-12) y revisión de todos los PRs.
- **Jueves en la tarde:** integro todo y cargo datos de demo. **A las 21:00 se congela `main`.**

**Raúl (Product Owner)**
- **Hoy:** acepta la invitación a Jira, pasa los issues de GitHub a Jira, define los puntos de entrega, confirma Bootstrap 5 y aprueba la Definición de Terminado.
- **Miércoles:** diseño general (base.html y barra de navegación).
- **Miércoles a jueves:** catálogo (HU-11).
- **Viernes:** guion de la demo y conducción de la Review.

**Santiago**
- **Hoy a miércoles 12:00:** PR pequeño con los campos `email_verificado` y `carrera`.
- **Hasta el jueves 12:00:** registro solo con `@upb.edu`, verificación por correo, login y logout (HU-01 y HU-02).

**Gonzalo**
- **Hoy desde las ~17:00 hasta el miércoles 12:00:** PR pequeño con los modelos de anuncios. **Es la entrega más crítica del sprint.**
- **Hasta el jueves 12:00:** formulario para publicar con 1 a 5 fotos y precio mayor a Bs 0 (HU-06).

## Calendario y ruta crítica

| Actividad | Quién | Espera a | Cuándo | Holgura |
|---|---|---|---|---|
| A. Integrar la rama `Santiago` a `main` | Uriel | — | hoy, antes de 13:00 | **0** |
| B. Fundación técnica (UP-46) en `main` | Uriel | A | hoy, hasta 17:00 | **0** |
| C. Modelos de anuncios en `main` | Gonzalo | B | mié 18, 12:00 | **0** |
| D. Publicar anuncio (HU-06) | Gonzalo | C | mié tarde → jue 12:00 | **0** |
| E1. Campos `email_verificado` y `carrera` | Santiago | A | mié 18, 12:00 | 1 día |
| E2. Registro, verificación, login y logout | Santiago | A, B | mar tarde → jue 12:00 | ½ día |
| F. Plantilla base real | Raúl | B | mié mañana | 1 día (todos usan la provisional) |
| G. Catálogo (HU-11) | Raúl | C (o el contrato de la sección 5) | mié → jue 12:00 | ½ día |
| H. Detalle (HU-12) | Uriel | C | mié tarde | 1 día (se recorta primero) |
| I. PostgreSQL local | cada uno | B | hasta el jue | 1½ días (hay respaldo en SQLite) |
| J. Integración, demo y **congelamiento a las 21:00** | Uriel y todos | D, E2, G | jue 19 tarde | **0** |
| K. Review y Retrospectiva | todos | J | vie 20 en la mañana | — |

**Ruta crítica: A → B → C → D → J → Review.** Si la fundación o los modelos se atrasan, se atrasan tres personas. **Quien vea que no llega a su hora avisa en el grupo apenas lo sepa, no al final.**

---

# PARTE 2 · Detalle (para no chocar)

## 3. Antes de empezar (TODOS, una sola vez)

1. **Instala:** Git, Python 3.12 o 3.13 (marca "Add python.exe to PATH"), PyCharm y PostgreSQL 17 o 18 (instalador de EDB, con pgAdmin; anota la contraseña del usuario `postgres`; puerto 5432). PostgreSQL puede esperar hasta el jueves, porque mientras tanto el proyecto funciona con SQLite.
2. **Jira:** acepta la invitación que te manda Uriel por correo y entra a https://urieltb2402.atlassian.net, proyecto **UP**.
3. **Espera el aviso de Uriel "main actualizado"** (hoy antes de las 13:00). Luego, según tu caso:
   - **Ya tienes el repo (Gonzalo, Santiago):**
     ```powershell
     cd C:\proyectos\upbuy          # o la carpeta donde lo tengas
     git checkout main
     git pull origin main
     del db.sqlite3                 # OBLIGATORIO: la base vieja usa el usuario por defecto de Django y ya no sirve
     ```
     Santiago, además: `git branch -D Santiago` (su contenido ya está en `main`).
   - **No tienes el repo (Raúl):**
     ```powershell
     git clone https://github.com/peterteranb/upbuy.git C:\proyectos\upbuy
     cd C:\proyectos\upbuy
     ```
4. **Entorno virtual:**
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
   En PyCharm: *Settings → Python Interpreter → Add Interpreter → Existing → `C:\proyectos\upbuy\.venv\Scripts\python.exe`*.
5. **Archivo `.env`** (nunca se sube a GitHub):
   ```powershell
   copy .env.example .env
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Pega la clave que sale en `SECRET_KEY=`. **No uses la clave vieja** que estaba en `settings.py`.
6. **Cuando Uriel avise "fundación en main"** (hoy, ~17:00):
   ```powershell
   git checkout main
   git pull origin main
   pip install -r requirements.txt
   ```
   **PostgreSQL:** crea la base `upbuy` (en pgAdmin: *Databases → Create → Database* → `upbuy`) y en `.env` pon:
   `DATABASE_URL=postgres://postgres:TU_CLAVE@localhost:5432/upbuy`
   Si tu clave tiene símbolos, escríbelos codificados (`@` → `%40`, `#` → `%23`). Si todavía no instalaste PostgreSQL, deja esa línea comentada y se usa SQLite.
7. **Probar que todo anda:**
   ```powershell
   python manage.py migrate
   python manage.py createsuperuser      # pide correo y contraseña
   python manage.py runserver
   ```
   Abre http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/.
8. **Git con tu identidad** (el mismo correo que usas en GitHub):
   `git config --global user.name "Tu Nombre"` y `git config --global user.email "tu-correo-de-github"`.

### Cada vez que te sientas a trabajar
```powershell
cd C:\proyectos\upbuy
.venv\Scripts\activate
git checkout main
git pull origin main
pip install -r requirements.txt
python manage.py migrate
git checkout TU-RAMA
git merge main                 # trae lo último de main a tu rama
```
En Jira, mueve tu historia a **In Progress** cuando empieces.

## 4. Reglas para no chocar

### 4.1 De quién es cada archivo (en el Sprint 1)

| Archivos | Dueño | Los demás… |
|---|---|---|
| `config/` (settings, urls), `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, `config/tests.py` | **Uriel** | piden el cambio a Uriel |
| `usuarios/` (todo), `templates/usuarios/` | **Santiago** | no tocan |
| `anuncios/` (todo), `templates/anuncios/` | **Gonzalo** | no tocan |
| `catalogo/views.py` → solo la función `lista` · `catalogo/tests.py` · `templates/catalogo/lista.html` · `templates/catalogo/_tarjeta_anuncio.html` | **Raúl** | no tocan |
| `templates/base.html`, `templates/partials/`, `static/` | **Raúl** (desde el mié; hoy Uriel deja la versión provisional) | no tocan |
| `catalogo/views.py` → solo la función `detalle` · `catalogo/tests_detalle.py` · `templates/catalogo/detalle.html` · `catalogo/management/` | **Uriel** | no tocan |

### 4.2 Ramas, commits y PR
- **Rama nueva, siempre desde `main` actualizado:** `git checkout main && git pull origin main && git checkout -b UP-19-modelos`
- **Commits con la clave de Jira al inicio:** `UP-19 Agrega modelo Anuncio`. Así Jira muestra ramas, commits y PRs dentro de cada historia.
- **Nadie hace push a `main`.** Todo entra por un **Pull Request** con 1 aprobación. Uriel revisa los PRs de los demás (responde en 3 horas como máximo, entre 08:00 y 22:00) y Santiago o Gonzalo revisan los de Uriel.
- **Título del PR:** `UP-19 Modelos de anuncios y categorías`. En la descripción va qué hace, cómo probarlo y una captura si es visual.
- **Antes de abrir un PR**, los tres comandos tienen que pasar:
  ```powershell
  python manage.py check
  python manage.py makemigrations --check --dry-run
  python manage.py test
  ```
- **Migraciones:** solo el dueño de una app crea migraciones de esa app. Nunca se edita una migración que ya está en `main`. Si `makemigrations` te genera una migración de otra app, **no la subas** y avisa.
- **Nunca se suben** `.env`, `db.sqlite3`, `media/`, `.venv/` ni `.idea/`.
- **Nadie hace `pip freeze > requirements.txt`.** Si necesitas un paquete, se lo pides a Uriel.
- **No uses "Reformat code" de PyCharm sobre archivos ajenos.** Cambia el formato de todo el archivo y genera conflictos.

### 4.3 Jira
**In Progress** al empezar. **Done** solo cuando cumple la Definición de Terminado (sección 7) y el PO lo verificó en la demo.

## 5. Contratos (lo que todos asumen)

### 5.1 URLs (las deja listas la fundación, con vistas provisionales)

| Nombre | Ruta | Dueño de la vista |
|---|---|---|
| `catalogo:lista` | `/` | Raúl |
| `catalogo:detalle` | `/anuncio/<pk>/` | Uriel |
| `anuncios:publicar` | `/anuncios/publicar/` | Gonzalo |
| `usuarios:registro` | `/cuenta/registro/` | Santiago |
| `usuarios:registro_enviado` | `/cuenta/registro/enviado/` | Santiago |
| `usuarios:verificar` | `/cuenta/verificar/<uidb64>/<token>/` | Santiago |
| `usuarios:login` | `/cuenta/login/` | Santiago |
| `usuarios:logout` | `/cuenta/logout/` (**solo POST**) | Santiago |

En las plantillas usa siempre `{% url 'catalogo:detalle' anuncio.pk %}` y nunca rutas escritas a mano.

### 5.2 Plantillas
- Todas empiezan con `{% extends "base.html" %}` y usan los bloques **`title`**, **`content`**, **`extra_css`** y **`extra_js`**.
- `base.html` ya muestra los mensajes de `django.contrib.messages`. No los repitas en tu plantilla.
- **Bootstrap 5.3** viene cargado desde un CDN en `base.html`, así que puedes usar sus clases en cualquier plantilla. Si Raúl elige otra librería, lo avisa hoy antes de las 20:00.
- Todo el texto va en español. Los precios se muestran así: `Bs {{ anuncio.precio|floatformat:2 }}` (se ve "Bs 25,00").

### 5.3 Configuración disponible (la deja la fundación)
- `settings.UPBUY_DOMINIO_CORREO = "@upb.edu"`
- `LOGIN_URL = "usuarios:login"` · `LOGIN_REDIRECT_URL = "catalogo:lista"` · `LOGOUT_REDIRECT_URL = "usuarios:login"`
- En desarrollo los correos se imprimen en la consola de `runserver`.
- `MEDIA_URL = "media/"`: las fotos se guardan en `media/` y se sirven solas con `DEBUG=True`.

### 5.4 Usuario (app `usuarios`, de Santiago)
`Usuario` inicia sesión con `email` (no tiene `username`) y usa `first_name` y `last_name`. Después del PR E1 de Santiago (mié 12:00) también tiene:
```python
email_verificado = models.BooleanField("correo verificado", default=False)
carrera = models.CharField("carrera", max_length=80, blank=True)
```

### 5.5 Modelos de anuncios (app `anuncios`, de Gonzalo): se copian tal cual
```python
from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "categorías"

    def __str__(self):
        return self.nombre


class Anuncio(models.Model):
    class Estado(models.TextChoices):          # estado de MODERACIÓN
        EN_REVISION = "en_revision", "En revisión"
        ACTIVO = "activo", "Activo"
        RECHAZADO = "rechazado", "Rechazado"
        VENDIDO = "vendido", "Vendido"

    class Condicion(models.TextChoices):       # el "estado" del PRODUCTO en HU-06
        NUEVO = "nuevo", "Nuevo"
        COMO_NUEVO = "como_nuevo", "Como nuevo"
        USADO = "usado", "Usado"

    class PuntoEntrega(models.TextChoices):    # PROVISIONAL: Raúl confirma la lista antes del mié 10:00
        ENTRADA_PRINCIPAL = "entrada_principal", "Entrada principal"
        BIBLIOTECA = "biblioteca", "Biblioteca"
        CAFETERIA = "cafeteria", "Cafetería"
        PARQUEO = "parqueo", "Parqueo"
        OTRO = "otro", "Otro (coordinar por chat)"

    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="anuncios")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="anuncios")
    titulo = models.CharField("título", max_length=80)
    descripcion = models.TextField("descripción", blank=True)
    precio = models.DecimalField("precio (Bs)", max_digits=10, decimal_places=2)
    condicion = models.CharField("estado del producto", max_length=12, choices=Condicion.choices)
    punto_entrega = models.CharField("punto de entrega", max_length=30, choices=PuntoEntrega.choices)
    horario_entrega = models.CharField("horario de entrega", max_length=80, blank=True,
                                       help_text="Ej.: lunes a viernes, 12:00 a 14:00")
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.ACTIVO)  # Sprint 2: EN_REVISION
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        constraints = [
            models.CheckConstraint(condition=models.Q(precio__gt=0), name="anuncio_precio_mayor_a_cero"),
        ]

    def __str__(self):
        return self.titulo


class FotoAnuncio(models.Model):
    anuncio = models.ForeignKey(Anuncio, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="anuncios/%Y/%m/")
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["orden"]
```
**Categorías iniciales** (se crean con una migración de datos): Entradas · Comida · Postres · Ropa · Libros · Tecnología · Servicios · Otros. Recordatorio: **no se permite vender tareas, trabajos ni tutorías.**

---

## 6. Detalle por persona

> Para trabajar con tu IA (Claude, ChatGPT, Copilot…), **pega tu bloque completo junto con las secciones 4 y 5 de este documento**. Tu bloque dice qué archivos tocas y cuáles no. Si tu IA propone tocar algo fuera de tu lista, **no lo hagas** y avisa en el grupo.

### 6.1 Santiago: UP-14 (HU-01) y UP-15 (HU-02)

```text
Trabajo en UPBuy: Django 5.2, Python, PostgreSQL. Repo github.com/peterteranb/upbuy, carpeta C:\proyectos\upbuy, Windows y PyCharm.
Mi parte del Sprint 1: HU-01 (Jira UP-14) y HU-02 (Jira UP-15), en la app `usuarios`, que ya existe:
modelo `Usuario(AbstractUser)` sin username, USERNAME_FIELD="email", AUTH_USER_MODEL="usuarios.Usuario", con su `UsuarioManager`.

ALCANCE. Solo toco: usuarios/ (models, admin, forms, views, urls, tests, migrations) y templates/usuarios/.
NO toco: config/, requirements.txt, templates/base.html, templates/partials/, static/, anuncios/, catalogo/.
Si necesito un setting o un paquete, se lo pido a Uriel. Todo el texto en español. Bootstrap 5.3 ya viene en base.html.
Las plantillas usan {% extends "base.html" %} y el bloque `content`.

PASO 1. PR pequeño, listo antes del miércoles 18 a las 12:00. Rama `UP-14-email-verificado`, desde main actualizado.
 1. En usuarios/models.py, agregar a Usuario:
      email_verificado = models.BooleanField("correo verificado", default=False)
      carrera = models.CharField("carrera", max_length=80, blank=True)
 2. python manage.py makemigrations usuarios  → genera usuarios/migrations/0002_... (no edito la 0001).
 3. usuarios/admin.py: agregar email_verificado y carrera a list_display, y email_verificado a list_filter.
 4. check, makemigrations --check y test pasan. Commit "UP-14 Campos email_verificado y carrera". PR a main.
    Gonzalo depende de este campo el jueves.

PASO 2. Rama `UP-14-registro-login` desde main, DESPUÉS de que Uriel avise "fundación en main".
La fundación deja usuarios/urls.py con app_name="usuarios" y estas rutas provisionales, que yo reemplazo:
 registro/ (name="registro"), registro/enviado/ (name="registro_enviado"),
 verificar/<uidb64>/<token>/ (name="verificar"), login/ (name="login"), logout/ (name="logout").
Settings disponibles: settings.UPBUY_DOMINIO_CORREO="@upb.edu", LOGIN_REDIRECT_URL="catalogo:lista",
LOGOUT_REDIRECT_URL="usuarios:login", EMAIL_BACKEND de consola en desarrollo, y MinimumLengthValidator de 8.

 a) usuarios/forms.py · RegistroForm, con campos first_name (obligatorio, "Nombre"), last_name (obligatorio, "Apellido"),
    email ("Correo institucional"), carrera (opcional), password1 y password2.
    - email: strip() y lower(). Solo es válido si termina EXACTAMENTE en settings.UPBUY_DOMINIO_CORREO.
      Rechazar @upb.edu.bo, @gmail.com, etc. Mensaje: "Usa tu correo institucional (@upb.edu)."
    - Correo ya registrado → "Ya existe una cuenta con este correo."
    - Contraseñas iguales y validadas con django.contrib.auth.password_validation.validate_password.
    - save(): crea el usuario con create_user y email_verificado=False.
 b) Vista `registro` (GET/POST). Si el formulario es válido: crea el usuario, envía el correo de verificación y
    redirige a usuarios:registro_enviado ("Te enviamos un enlace a tu correo"). No inicia sesión sola.
    - Enlace: uidb64 = urlsafe_base64_encode(force_bytes(user.pk)); token = default_token_generator.make_token(user);
      url = request.build_absolute_uri(reverse("usuarios:verificar", args=[uidb64, token])).
    - send_mail con asunto "Verifica tu cuenta de UPBuy" y cuerpo desde templates/usuarios/correo_verificacion.txt.
      En desarrollo el correo con el enlace aparece en la consola de runserver.
 c) Vista `verificar(uidb64, token)`. Si es válido: email_verificado=True, messages.success("Tu correo fue verificado.")
    y redirige a usuarios:login. Si no: plantilla usuarios/verificacion_invalida.html con
    "El enlace no es válido o ya fue usado."
 d) Login: django.contrib.auth.views.LoginView con template_name="usuarios/login.html" y un AuthenticationForm
    propio, con etiqueta "Correo institucional" y error invalid_login = "Correo o contraseña incorrectos.".
    La sesión se mantiene al recargar (comportamiento normal de Django).
 e) Logout: LogoutView. En Django 5 SOLO acepta POST. El botón de cerrar sesión (navbar de Raúl) es un
    <form method="post" action="{% url 'usuarios:logout' %}"> con {% csrf_token %}. Redirige a usuarios:login.
 f) Plantillas en templates/usuarios/: registro.html, registro_enviado.html, login.html (con enlace
    "¿No tienes cuenta? Regístrate"), verificacion_invalida.html y correo_verificacion.txt.
    Errores visibles por campo. Se ven bien a 360 px.
 g) usuarios/tests.py (TestCase), con estas pruebas:
    1. @gmail.com rechazado  2. @upb.edu.bo rechazado  3. contraseña de 7 caracteres rechazada
    4. correo duplicado rechazado  5. registro válido: crea el usuario con email_verificado=False y len(mail.outbox)==1
    6. el enlace del correo verifica  7. un token alterado NO verifica
    8. login correcto redirige a "/"  9. login incorrecto muestra "Correo o contraseña incorrectos."
    10. logout por POST redirige a /cuenta/login/
 h) check, makemigrations --check y test pasan.
    Commits "UP-14 ..." o "UP-15 ...". PR "UP-14 UP-15 Registro, verificación e inicio de sesión", listo el jueves 19 a las 12:00.

FUERA DE ALCANCE: recuperar contraseña (HU-03), foto y edición de perfil (HU-04), SMTP real
(Uriel lo configura el jueves si alcanza), impedir publicar sin verificar (eso lo hace Gonzalo con mi campo).
```

### 6.2 Gonzalo: UP-19 (HU-06)

```text
Trabajo en UPBuy: Django 5.2, Python, PostgreSQL. Repo github.com/peterteranb/upbuy, carpeta C:\proyectos\upbuy, Windows y PyCharm.
Mi parte del Sprint 1: HU-06 "Publicar un anuncio" (Jira UP-19), en la app `anuncios`.
La app la crea vacía Uriel en la fundación (ya registrada en INSTALLED_APPS, con anuncios/urls.py,
app_name="anuncios" y la ruta "publicar/" name="publicar" apuntando a una vista provisional que yo reemplazo).

ALCANCE. Solo toco: anuncios/ (models, admin, forms, views, urls, tests, migrations) y templates/anuncios/.
NO toco: config/, requirements.txt (Pillow ya viene en la fundación), usuarios/, catalogo/, templates/base.html, static/.
Todo el texto en español. Bootstrap 5.3 ya viene en base.html.

PASO 1. ENTREGA MÁS CRÍTICA DEL SPRINT: PR listo antes del miércoles 18 a las 12:00.
Rama `UP-19-modelos`, desde main con la fundación.
 1. anuncios/models.py: copiar EXACTO el contrato de la sección 5.5 (Categoria, Anuncio, FotoAnuncio).
    Raúl (catálogo) y Uriel (detalle) programan con esos nombres de campos.
    Si Raúl cambia la lista de puntos de entrega antes del miércoles a las 10:00, solo cambio esas opciones.
 2. python manage.py makemigrations anuncios  → 0001_initial.
 3. Migración de datos 0002_categorias_iniciales (python manage.py makemigrations anuncios --empty -n categorias_iniciales),
    con RunPython que crea, usando apps.get_model, las categorías Entradas, Comida, Postres, Ropa, Libros,
    Tecnología, Servicios y Otros (slug con slugify: "tecnologia", etc.), y una función reversa que las borra.
 4. anuncios/admin.py: CategoriaAdmin con prepopulated_fields={"slug": ("nombre",)}.
    AnuncioAdmin con list_display (titulo, vendedor, categoria, precio, estado, creado), list_filter (estado, categoria),
    search_fields (titulo, descripcion) y un TabularInline de FotoAnuncio.
 5. anuncios/tests.py: (a) existen las 8 categorías; (b) crear un Anuncio con precio=0 lanza IntegrityError
    (usar with transaction.atomic()); (c) __str__ devuelve el título.
 6. check, makemigrations --check y test pasan. Commit "UP-19 Modelos de anuncios y categorías". PR a main.
    Si veo que no llego a las 12:00, aviso en el grupo en ese momento.

PASO 2. Rama `UP-19-publicar-anuncio` desde main, ya con mis modelos fusionados. PR listo el jueves 19 a las 12:00.
 a) anuncios/forms.py
    - Campo de varias fotos (patrón de la documentación de Django):
        class MultipleFileInput(forms.ClearableFileInput):
            allow_multiple_selected = True
        class MultipleImageField(forms.ImageField):
            def __init__(self, *args, **kwargs):
                kwargs.setdefault("widget", MultipleFileInput(attrs={"accept": "image/*"}))
                super().__init__(*args, **kwargs)
            def clean(self, data, initial=None):
                single = super().clean
                if isinstance(data, (list, tuple)):
                    return [single(d, initial) for d in data]
                return [single(data, initial)] if data else []
    - AnuncioForm(ModelForm) con fields = titulo, descripcion, categoria, precio, condicion, punto_entrega,
      horario_entrega, más fotos = MultipleImageField(required=False, label="Fotos (1 a 5)").
    - precio: MinValueValidator(Decimal("0.01"), "El precio debe ser mayor a Bs 0.").
    - clean_fotos(): entre 1 y 5 fotos → si no, "Sube entre 1 y 5 fotos."; cada foto pesa 5 MB como máximo → si no,
      "Cada foto debe pesar 5 MB o menos."
 b) anuncios/views.py · publicar:
    - @login_required.
    - Si not request.user.email_verificado → messages.warning("Verifica tu correo para poder publicar.")
      y redirect("catalogo:lista"). (El campo lo agrega Santiago el miércoles a las 12:00.)
    - POST: AnuncioForm(request.POST, request.FILES). Si es válido, dentro de transaction.atomic():
      anuncio = form.save(commit=False); anuncio.vendedor = request.user; anuncio.estado = Anuncio.Estado.ACTIVO;
      anuncio.save(); por cada foto (i, f): FotoAnuncio.objects.create(anuncio=anuncio, imagen=f, orden=i).
      messages.success("Tu anuncio fue publicado.") y redirect("catalogo:detalle", pk=anuncio.pk).
    - El vendedor SIEMPRE es request.user (nunca sale del formulario).
 c) templates/anuncios/publicar.html: extends base.html; <form method="post" enctype="multipart/form-data">,
    {% csrf_token %}, errores por campo, precio con prefijo "Bs" y botón "Publicar". Se ve bien a 360 px.
 d) anuncios/tests.py (usar @override_settings(MEDIA_ROOT=tempfile.mkdtemp()) y una imagen PNG pequeña
    creada con Pillow en un SimpleUploadedFile):
    1. usuario anónimo → redirige al login  2. usuario sin verificar → no crea el anuncio
    3. precio 0 → error  4. sin fotos → error  5. 6 fotos → error
    6. publicación válida → crea 1 Anuncio ACTIVO con sus FotoAnuncio en orden y redirige a /anuncio/<pk>/
 e) check, makemigrations --check y test pasan. Commits "UP-19 ...". PR "UP-19 Publicar anuncio con fotos".

FUERA DE ALCANCE: editar o eliminar (HU-07), moderación (Sprint 2: allí el estado inicial pasa a EN_REVISION),
preventas, guardar las fotos en la nube.
```

### 6.3 Raúl: Product Owner y UP-24 (HU-11)

**Como Product Owner (hoy):**
1. Acepta la invitación a Jira.
2. Revisa el Sprint Backlog (UP-46, 14, 15, 19, 24 y 25) y su orden. La documentación del sprint está en **UP-47**.
3. **Pasa tus issues de GitHub a Jira.** Por cada issue: si ya existe la historia o tarea en Jira, comenta "Se gestiona en Jira: UP-xx" y ciérralo; si es trabajo nuevo, créalo en el backlog de Jira y cierra el issue. Desde hoy, **el backlog vive solo en Jira.**
4. **Puntos de entrega:** confirma o corrige la lista de la sección 5.5 **antes del miércoles a las 10:00** (en el grupo y como comentario en UP-19).
5. Aprueba o ajusta la **Definición de Terminado** (sección 7).
6. Confirma **Bootstrap 5.3** como librería de interfaz, o elige otra **hoy antes de las 20:00**.
7. Recuerda que **HU-12 pide la carrera del vendedor**: por eso Santiago la agrega como campo opcional en el registro.

**Como developer:**

```text
Trabajo en UPBuy: Django 5.2, Python, PostgreSQL. Repo github.com/peterteranb/upbuy, carpeta C:\proyectos\upbuy, Windows y PyCharm.
Mi parte del Sprint 1: el diseño general y HU-11 "Ver el catálogo por categorías y lo recién publicado" (Jira UP-24).

ALCANCE. Solo toco: templates/base.html, templates/partials/, static/css/upbuy.css, static/img/,
la FUNCIÓN `lista` de catalogo/views.py (no toco la función `detalle`, que es de Uriel),
catalogo/tests.py, templates/catalogo/lista.html y templates/catalogo/_tarjeta_anuncio.html.
NO toco: config/, requirements.txt, usuarios/, anuncios/, templates/catalogo/detalle.html, catalogo/tests_detalle.py.
Todo el texto en español. Bootstrap 5.3 desde CDN.

PASO 1. Rama `UP-24-plantilla-base` desde main con la fundación. PR listo el miércoles 18 a las 12:00.
 - Reemplazar templates/base.html (la provisional de Uriel) MANTENIENDO: {% load static %}, <html lang="es">,
   meta viewport, el CSS y el JS bundle de Bootstrap 5.3, el enlace a static/css/upbuy.css,
   el include de mensajes y los bloques title, extra_css, content y extra_js.
 - templates/partials/_navbar.html: logo "UPBuy" → {% url 'catalogo:lista' %}; navbar-expand-md con menú
   desplegable en el celular. Con sesión: botón "Publicar" → {% url 'anuncios:publicar' %}, el nombre del usuario
   y "Cerrar sesión" como <form method="post" action="{% url 'usuarios:logout' %}">{% csrf_token %}…</form>
   (el logout solo funciona por POST). Sin sesión: "Iniciar sesión" → usuarios:login y "Crear cuenta" → usuarios:registro.
 - templates/partials/_mensajes.html: muestra messages como alertas de Bootstrap que se pueden cerrar.
 - static/css/upbuy.css: variables CSS con los colores de la UPB (--upb-primario, etc.), un pie de página simple
   y nada de estilos que rompan Bootstrap.
 - Probar a 360 px en Chrome (F12 → modo dispositivo): sin scroll horizontal.
 - Commit "UP-24 Plantilla base". PR a main.

PASO 2. Rama `UP-24-catalogo` desde main. PR listo el jueves 19 a las 12:00.
Los modelos de Gonzalo llegan a main el miércoles a las 12:00. Antes de eso puedo armar la plantilla con
los nombres de campo del contrato (sección 5.5).
 - catalogo/views.py · lista(request):
     qs = Anuncio.objects.filter(estado=Anuncio.Estado.ACTIVO).select_related("categoria", "vendedor").prefetch_related("fotos")
     (el orden "más reciente primero" ya viene del Meta de Anuncio)
     Filtro opcional ?categoria=<slug> → qs.filter(categoria__slug=slug).
     Paginator de 12 con ?page=. Contexto: page_obj, categorias (Categoria.objects.all()), categoria_actual.
 - templates/catalogo/lista.html: botones de categoría ("Todas" + una por categoría, con la activa marcada),
   grilla "row row-cols-1 row-cols-sm-2 row-cols-lg-4 g-3", paginación y estado vacío:
   "Todavía no hay anuncios en esta categoría."
 - templates/catalogo/_tarjeta_anuncio.html: la primera foto ({{ anuncio.fotos.all.0.imagen.url }}, o una imagen
   de reemplazo si no hay), "Bs {{ anuncio.precio|floatformat:2 }}", el título, {{ anuncio.get_punto_entrega_display }}
   y un enlace a {% url 'catalogo:detalle' anuncio.pk %}. Usar fotos.all.0 y no fotos.first, para que sirva
   el prefetch.
 - catalogo/tests.py: 1. solo aparecen anuncios ACTIVO  2. el más reciente sale primero
   3. el filtro por categoría funciona  4. sin anuncios aparece el mensaje vacío.
 - Probar a 360 px. check, makemigrations --check y test pasan. Commits "UP-24 ...". PR "UP-24 Catálogo".
 - Si hay conflicto en catalogo/views.py con la función `detalle` de Uriel, conservar las dos funciones.

FUERA DE ALCANCE: búsqueda, filtros por precio o estado y orden (Sprint 2), detalle del anuncio (Uriel).
```

**Viernes:** prepara el guion de la demo (registro → verificación → login → publicar con fotos → verlo primero en el catálogo → filtrar → abrir el detalle → logout) y conduce la Review con el docente usando el tablero y el burndown de Jira.

### 6.4 Uriel: UP-46, UP-25, revisiones e integración
En resumen:
- **Hoy:** invitar al equipo a Jira, iniciar el Sprint 1, integrar la rama de Santiago y dejar la fundación en `main` antes de las 17:00.
- **Miércoles:** PostgreSQL local, revisar los PRs (respuesta en 3 horas como máximo) y hacer HU-12 en `UP-25-detalle`.
- **Jueves en la tarde:** integración, comando `cargar_demo`, prueba completa, **congelamiento a las 21:00** y etiqueta `sprint-1`.

## 7. Definición de Terminado (propuesta; la aprueba el PO)
Una historia está **terminada** cuando:
1. Cumple **todos** sus criterios de aceptación de Jira y el PO los verificó.
2. Está en `main` mediante un PR aprobado por otro integrante.
3. `python manage.py test` pasa, y cada regla de negocio nueva (dominio del correo, precio > 0, cantidad de fotos, etc.) tiene su prueba.
4. `python manage.py makemigrations --check --dry-run` no detecta cambios pendientes.
5. El repositorio no tiene claves, `.env`, `db.sqlite3` ni `media/`.
6. La interfaz está en español y se usa bien a **360 px** de ancho, sin scroll horizontal.
7. La historia está en **Done** en Jira.

## 8. Eventos del Sprint
- **Daily Scrum:** 15 minutos, miércoles 18 y jueves 19 (hora a confirmar; propuesta: 20:00, por Meet o Discord). Cada uno dice qué terminó, qué hará y qué lo bloquea. Si alguien no puede conectarse, lo escribe en el grupo antes de esa hora.
- **Congelamiento:** jueves 19 a las 21:00. Después de esa hora solo entran a `main` los arreglos de integración de Uriel.
- **Sprint Review:** viernes 20, antes de las 12:00 (hora a confirmar). Demo en vivo con el docente.
- **Retrospectiva:** viernes 20, después de la Review.

## 9. Riesgos y plan B

| Riesgo | Señal | Plan B |
|---|---|---|
| Los modelos de anuncios (Gonzalo) se atrasan | No hay PR el miércoles a las 12:00 | Uriel los termina, porque el contrato ya está escrito; Gonzalo sigue con el formulario |
| Problemas instalando PostgreSQL | Errores de conexión | Seguir con SQLite hasta el jueves; Uriel integra y hace la demo en PostgreSQL |
| No hay correo real para la verificación | El SMTP no está listo el jueves | Demo con el enlace impreso en la consola; el PO decide si acepta HU-01 así |
| Un PR necesita un arreglo | Revisión con cambios | Si es pequeño (menos de 30 min), lo arregla Uriel. Si es de la lógica de la historia, lo arregla el autor en 3 horas como máximo; si no responde, lo toma Uriel |
| HU-12 no llega | El jueves a las 12:00 no está | Vuelve al backlog del Sprint 2 sin afectar el objetivo |
