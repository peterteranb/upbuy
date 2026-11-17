# UPBuy

Marketplace web de la comunidad de la Universidad Privada Boliviana (UPB): los estudiantes,
registrados con su correo institucional `@upb.edu`, publican anuncios (comida, entradas, ropa,
libros, tecnología, etc.) y coordinan la entrega dentro del campus.

Hecho con **Django 5.2**, **Bootstrap 5.3** y **PostgreSQL** (con SQLite como respaldo en desarrollo).

- Plan del Sprint 1 (roles, contratos y reglas): [docs/sprint-1/PLAN-SPRINT-1.md](docs/sprint-1/PLAN-SPRINT-1.md)
- Jira: proyecto `UP` · GitHub: https://github.com/peterteranb/upbuy

## Requisitos

- Python **3.12 o 3.13** (al instalar, marca "Add python.exe to PATH")
- Git
- PostgreSQL **17 o 18** (opcional: sin él, el proyecto usa SQLite)

## Instalación en Windows (PowerShell)

```powershell
git clone https://github.com/peterteranb/upbuy.git C:\proyectos\upbuy
cd C:\proyectos\upbuy

# 1. Entorno virtual y dependencias
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Variables de entorno
copy .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
#    Pega la clave generada en SECRET_KEY= dentro de .env

# 3. (Opcional) PostgreSQL: crea la base "upbuy" en pgAdmin y descomenta en .env
#    DATABASE_URL=postgres://postgres:TU_CLAVE@localhost:5432/upbuy
#    Si la clave tiene símbolos, codifícalos (@ -> %40, # -> %23).

# 4. Base de datos, administrador y servidor
python manage.py migrate
python manage.py createsuperuser      # pide correo y contraseña
python manage.py runserver
```

Abre http://127.0.0.1:8000/ y http://127.0.0.1:8000/admin/.

En desarrollo los correos (por ejemplo, el de verificación) se imprimen en la consola de `runserver`.

### Cada vez que te sientas a trabajar

```powershell
cd C:\proyectos\upbuy
.venv\Scripts\activate
git checkout main
git pull origin main
pip install -r requirements.txt
python manage.py migrate
git checkout TU-RAMA
git merge main
```

## Reglas del equipo (resumen)

Detalle completo en la sección 4 del [plan del sprint](docs/sprint-1/PLAN-SPRINT-1.md).

- **Ramas:** siempre desde `main` actualizado, con la clave de Jira: `UP-19-modelos`.
- **Commits:** empiezan con la clave de Jira: `UP-19 Agrega modelo Anuncio`.
- **Nadie hace push a `main`.** Todo entra por Pull Request con 1 aprobación.
  Título del PR: `UP-19 Modelos de anuncios y categorías`; en la descripción, qué hace, cómo probarlo y una captura si es visual.
- **Antes de abrir un PR** deben pasar:
  ```powershell
  python manage.py check
  python manage.py makemigrations --check --dry-run
  python manage.py test
  ```
- **Migraciones:** solo el dueño de una app crea migraciones de esa app; nunca se edita una migración que ya está en `main`.
- **Cada archivo tiene dueño** (tabla 4.1 del plan): no edites archivos ajenos; pide el cambio a su dueño.
- **Nunca se suben** `.env`, `db.sqlite3`, `media/`, `.venv/` ni `.idea/`.
- **Nadie hace `pip freeze > requirements.txt`.** Si necesitas un paquete, pídeselo a Uriel.
- **No uses "Reformat code" de PyCharm** sobre archivos ajenos.

## Estructura

| Carpeta | Contenido |
|---|---|
| `config/` | settings, URLs principales y pruebas del contrato de URLs |
| `usuarios/` | usuario propio (login con correo), registro y verificación |
| `anuncios/` | categorías, anuncios y fotos; publicar anuncio |
| `catalogo/` | lista de anuncios y detalle |
| `templates/` | `base.html`, parciales y plantillas por app |
| `static/` | CSS e imágenes propias |
