# UPBuy · Sprint 2

**Fechas:** miércoles 25 nov → **viernes 4 dic, 12:00** (Review en clase).
**Objetivo:** los anuncios pasan por moderación antes de publicarse, se encuentran con búsqueda y filtros, y el vendedor gestiona sus anuncios y su perfil.
**Roles:** PO Raúl · SM Uriel · Developers: los cuatro.

## Sprint Backlog (24 pts)

| Jira | Historia | Pts | Responsable | Ramas |
|---|---|---|---|---|
| UP-48 | Fundación del Sprint 2 (bloqueante) | — | Uriel | `UP-48-fundacion-s2` |
| UP-29 | HU-16 Aprobar o rechazar anuncios con motivo | 5 | Uriel | `UP-29-moderacion` |
| UP-30 | HU-17 Ver el estado de mi anuncio y el motivo de rechazo | 2 | Gonzalo | `UP-30-mis-anuncios` |
| UP-20 | HU-07 Editar o eliminar mis anuncios | 3 | Gonzalo | `UP-20-editar-eliminar` |
| UP-26 | HU-13 Buscar por palabra clave | 3 | Raúl | `UP-26-busqueda` |
| UP-27 | HU-14 Filtrar por categoría, precio, estado y punto de entrega | 5 | Raúl | `UP-27-filtros` |
| UP-17 | HU-04 Completar mi perfil (foto y carrera) | 3 | Santiago | `UP-17-perfil` |
| UP-33 | HU-20 Denunciar un anuncio o a un usuario | 3 | Santiago | `UP-33-denuncias` |

## Calendario

| Cuándo | Qué |
|---|---|
| **Mié 25, 21:00** | Fundación (UP-48) en main. **Nadie crea su rama antes de esto.** |
| Jue 26 – Vie 27 | Cada uno hace su **primera historia**. |
| **Vie 27, 20:00** | **PR de la primera historia** (Gonzalo UP-30, Raúl UP-26, Santiago UP-17, Uriel UP-29). |
| Sáb 28 – Lun 30 | Segunda historia. |
| **Lun 30, 20:00** | **PR de la segunda historia** (Gonzalo UP-20, Raúl UP-27, Santiago UP-33). |
| Mar 1 – Mié 2 | Correcciones e integración (Uriel). |
| **Jue 3, 20:00** | Congelamiento: etiqueta `sprint-2`. |
| Vie 4 | Review y Retro en clase. |

**Ruta crítica:** fundación (Uriel) → moderación (Uriel) → mis anuncios con estado (Gonzalo) → integración. Holgura: 1 día y medio (mar 1 – mié 2).

**Reglas que cambian respecto del Sprint 1:**
- Cada PR se revisa e integra en **menos de 2 horas** (lo hace Uriel; los de Uriel, cualquiera).
- Si un PR no llega en su fecha, Uriel toma esa historia al día siguiente.
- Las demás reglas del Sprint 1 siguen igual (sección 4 de `docs/sprint-1/PLAN-SPRINT-1.md`): ramas desde main, commits con la clave de Jira, `check` + `makemigrations --check` + `test` antes del PR, y solo el dueño de una app crea sus migraciones.

## Antes de empezar (todos, después de la fundación)
```powershell
cd C:\proyectos\upbuy
.venv\Scripts\activate
git checkout main
git pull origin main
pip install -r requirements.txt
python manage.py migrate
git checkout -b <tu-rama>
```

---

## Contratos (lo que deja la fundación)

### Modelo `Anuncio` (cambios)
```python
estado = models.CharField(..., default=Estado.EN_REVISION)   # antes ACTIVO
motivo_rechazo = models.TextField("motivo de rechazo", blank=True)
revisado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="anuncios_revisados")
revisado_en = models.DateTimeField("revisado en", null=True, blank=True)
```
- Al **publicar**, el anuncio queda `EN_REVISION`, aparece el mensaje "Tu anuncio fue enviado a revisión." y la vista redirige a `anuncios:mis_anuncios`.
- El catálogo y el detalle solo muestran los anuncios `ACTIVO` (igual que en el Sprint 1).
- Solo el usuario `is_staff` modera.

### URLs nuevas (con vistas provisionales que cada dueño reemplaza)
| Nombre | Ruta | Dueño |
|---|---|---|
| `anuncios:mis_anuncios` | `/anuncios/mios/` | Gonzalo |
| `anuncios:editar` | `/anuncios/<pk>/editar/` | Gonzalo |
| `anuncios:eliminar` | `/anuncios/<pk>/eliminar/` (solo POST) | Gonzalo |
| `usuarios:perfil` | `/cuenta/perfil/` | Santiago |
| `denuncias:crear` | `/denuncias/anuncio/<pk>/` | Santiago |
| `moderacion:cola` | `/moderacion/` | Uriel |
| `moderacion:revisar` | `/moderacion/<pk>/` | Uriel |

### Plantillas compartidas
- `templates/usuarios/_tarjeta_vendedor.html`: la tarjeta "Vendedor" sale de `detalle.html` a este archivo. Recibe `vendedor`. **Dueño: Santiago.**
- `templates/denuncias/_boton_denunciar.html`: queda vacía y `detalle.html` la incluye. Recibe `anuncio`. **Dueño: Santiago.**
- La barra de navegación suma "Mis anuncios", "Mi perfil" y "Moderación" (este último solo si `user.is_staff`). **Dueño: Raúl.**

### Archivos de cada uno en este sprint
| Archivos | Dueño |
|---|---|
| `config/`, `requirements.txt`, `anuncios/models.py` y migraciones de `anuncios`, `moderacion/`, `templates/moderacion/`, `catalogo/views.py` (función `detalle`), `detalle.html`, `cargar_demo` | Uriel |
| `anuncios/views.py`, `forms.py`, `urls.py` y `tests.py` (excepto la vista `publicar`), `templates/anuncios/` | Gonzalo |
| `catalogo/views.py` (función `lista`), `catalogo/forms.py` (nuevo), `catalogo/tests.py`, `templates/catalogo/lista.html` y `_tarjeta_anuncio.html`, `templates/partials/` | Raúl |
| `usuarios/` (incluye el modelo y sus migraciones), `templates/usuarios/`, `denuncias/`, `templates/denuncias/` | Santiago |

---

## Qué hace cada uno

### Uriel

**1. Fundación (UP-48), hoy hasta las 21:00.** Rama `UP-48-fundacion-s2`.
- Cambios de `Anuncio` (ver contratos) + migración.
- `publicar` deja el anuncio en revisión y redirige a "Mis anuncios"; actualizar su test.
- `startapp moderacion` y `startapp denuncias`, registradas, con `urls.py` y vistas provisionales para todas las URLs nuevas.
- Sacar la tarjeta del vendedor a `usuarios/_tarjeta_vendedor.html`, crear `denuncias/_boton_denunciar.html` vacía e incluir ambas en `detalle.html`.
- Enlaces nuevos en la barra de navegación.
- `cargar_demo`: los 12 anuncios siguen `ACTIVO`; agregar 3 en `EN_REVISION` para la demo de moderación. Agregar también un usuario `moderador@upb.edu` con `is_staff=True`.
- Test de que todas las URLs nuevas resuelven.
- Integrar a main y avisar.

**2. Moderación (UP-29), PR vie 27.** Rama `UP-29-moderacion`. App `moderacion`.
- `cola`: solo para staff (si no es staff, 403 o redirección al login). Lista los anuncios `EN_REVISION`, del más antiguo al más nuevo, con la primera foto, título, precio, vendedor y fecha. Si la cola está vacía, muestra "No hay anuncios pendientes".
- `revisar`: muestra el anuncio completo (fotos, datos, vendedor) con dos acciones por POST:
  - **Aprobar** → `ACTIVO`, borra el `motivo_rechazo`, guarda `revisado_por` y `revisado_en`.
  - **Rechazar** → exige motivo (formulario; sin motivo da error) → `RECHAZADO` con el motivo y los mismos datos de revisión.
  - Después vuelve a la cola con un mensaje.
- Solo se pueden revisar anuncios `EN_REVISION`; los demás dan 404.
- Tests: un usuario que no es staff no entra; aprobar lo deja ACTIVO y aparece en el catálogo; rechazar sin motivo da error; rechazar con motivo deja RECHAZADO y no aparece en el catálogo; un anuncio ya revisado da 404.

**3. Revisar e integrar** los PRs de los demás (menos de 2 h cada uno). **Mar 1 – mié 2:** integración, prueba completa y `cargar_demo` actualizado.

### Gonzalo

**1. Mis anuncios (UP-30), PR vie 27.** Rama `UP-30-mis-anuncios`.
- Vista `mis_anuncios` (`@login_required`): los anuncios de `request.user`, de todos los estados, del más nuevo al más viejo.
- Cada fila o tarjeta lleva: foto, título, precio, **etiqueta de estado** con color (En revisión = amarillo, Activo = verde, Rechazado = rojo, Vendido = gris) y fecha.
- Si está **Rechazado**, muestra el `motivo_rechazo` en un recuadro rojo.
- Si está Activo, enlace a su detalle. Botones "Editar" y "Eliminar" (apuntan a las URLs del contrato).
- Estado vacío: "Todavía no publicaste nada" con un botón para publicar.
- Tests: solo ves tus anuncios; se ven los 4 estados; el rechazado muestra el motivo; un anónimo va al login.

**2. Editar y eliminar (UP-20), PR lun 30.** Rama `UP-20-editar-eliminar`.
- `editar`: el mismo `AnuncioForm` precargado. Las fotos son **opcionales**: si sube nuevas (1 a 5), reemplazan a las anteriores; si no sube nada, se quedan las que había.
- Al guardar: estado vuelve a `EN_REVISION`, se limpia `motivo_rechazo` y aparece el mensaje "Cambios guardados. Tu anuncio volvió a revisión." → redirige a Mis anuncios.
- `eliminar`: **solo POST**, con confirmación (modal de Bootstrap o página "¿Seguro?"). Borra el anuncio y los archivos de sus fotos → Mis anuncios con un mensaje.
- **Solo el dueño** puede editar o eliminar: para cualquier otro usuario, 404 (usar `get_object_or_404(Anuncio, pk=pk, vendedor=request.user)`).
- No se puede editar un anuncio `VENDIDO` (404 o un mensaje).
- Tests: otro usuario recibe 404; al editar vuelve a EN_REVISION y se borra el motivo; editar sin fotos conserva las anteriores; editar con fotos las reemplaza; eliminar por GET no borra; eliminar por POST borra el anuncio y sus archivos.

**No toques** `anuncios/models.py` ni sus migraciones (son de Uriel); si necesitas un cambio, pídelo.

### Raúl

**Como PO:** confirmar este backlog y su orden. Decidir si "Ordenar resultados" (UP-28, 2 pts) entra si sobra tiempo.

**1. Búsqueda (UP-26), PR vie 27.** Rama `UP-26-busqueda`.
- Barra de búsqueda arriba del catálogo (GET `?q=`).
- Busca en `titulo` y `descripcion` (`Q(titulo__icontains=q) | Q(descripcion__icontains=q)`), solo entre los anuncios ACTIVOS.
- Se combina con `?categoria=` y la paginación conserva `q`.
- Si no hay resultados: "No encontramos anuncios para «{q}»", con un enlace para limpiar la búsqueda.
- Tests: encuentra por título y por descripción, no distingue mayúsculas, sin resultados muestra el mensaje, y la búsqueda se combina con la categoría.

**2. Filtros (UP-27), PR lun 30.** Rama `UP-27-filtros`.
- `catalogo/forms.py`: `FiltroCatalogoForm` (GET) con `q`, `categoria`, `precio_min`, `precio_max`, `estado_producto` y `punto_entrega`, todos opcionales. Si `precio_min > precio_max`, da error.
- En el celular, los filtros van en un panel desplegable (Bootstrap collapse u offcanvas); en escritorio, en una columna o fila.
- **Los filtros se combinan** entre sí y con la búsqueda.
- **Filtros activos visibles** como etiquetas con una "×" que quita **solo ese filtro** (enlace que conserva los demás parámetros), más un botón "Limpiar todo".
- La paginación conserva todos los filtros.
- Tests: cada filtro por separado, dos filtros combinados, el rango de precio, el error de mínimo > máximo y que quitar un filtro conserva los demás.

**No toques** la función `detalle`. La barra de navegación es tuya: si quieres, ajusta el estilo de los enlaces nuevos.

### Santiago

**1. Perfil (UP-17), PR vie 27.** Rama `UP-17-perfil`.
- `Usuario.foto = models.ImageField("foto", upload_to="perfiles/%Y/%m/", blank=True)` + migración.
- Vista `perfil` (`@login_required`, GET/POST) para editar nombre, apellido, carrera y foto. El correo se muestra pero no se edita.
- Carrera: lista desplegable con las carreras de la UPB (constante `CARRERAS` en `usuarios/forms.py`; el campo del modelo sigue siendo texto, **sin migración por esto**) + la opción "Otra".
- Foto: solo imagen, de 2 MB como máximo; si sube otra, se borra la anterior.
- `usuarios/_tarjeta_vendedor.html`: muestra la foto redonda (o un círculo con la inicial si no tiene), el nombre y la carrera. Así "los cambios se ven en mis anuncios".
- Tests: editar nombre y carrera, subir foto, rechazar un archivo que no es imagen o que es muy pesado, que un anónimo va al login y que la tarjeta del detalle muestra la foto o la inicial.

**2. Denuncias (UP-33), PR lun 30.** Rama `UP-33-denuncias`. App `denuncias` (ya creada vacía).
- Modelo `Denuncia`: `denunciante` (FK usuario), `anuncio` (FK, opcional), `usuario_denunciado` (FK usuario, opcional), `motivo` (choices: "Producto o servicio prohibido (tareas, trabajos, tutorías)", "Posible estafa", "Contenido inapropiado", "Precio engañoso", "Otro"), `detalle` (texto opcional), `creada_en`, `atendida` (bool, por defecto False).
- Vista `crear` (`@login_required`) en `/denuncias/anuncio/<pk>/`. Formulario con **qué denuncia** ("este anuncio" o "al vendedor"), el motivo de la lista y el detalle. Guarda y vuelve al detalle con "Gracias, el administrador revisará tu denuncia."
- No puedes denunciar tu propio anuncio. Una sola denuncia por usuario y anuncio (si repite, muestra un mensaje).
- `denuncias/_boton_denunciar.html`: enlace discreto "Denunciar" visible solo con sesión iniciada y si no eres el vendedor.
- **El administrador ve la denuncia:** `DenunciaAdmin` con `list_display` (creada_en, motivo, anuncio, usuario_denunciado, denunciante, atendida), filtros por motivo y atendida, y una acción "Marcar como atendida".
- Tests: denunciar el anuncio, denunciar al vendedor, que no puedes denunciarte a ti mismo, que no se duplica, que un anónimo va al login y que el botón no aparece para el dueño.

---

## Definición de Terminado (igual que en el Sprint 1)
1. Cumple todos los criterios de aceptación de Jira.
2. Está en main por un PR revisado.
3. Los tests pasan y cada regla nueva tiene su prueba.
4. `makemigrations --check` no muestra cambios pendientes.
5. Está en español y funciona bien a 360 px.
6. La historia está en Done en Jira.

## Fuera del Sprint 2
Ordenar resultados (UP-28, salvo que el PO lo meta), suspender usuarios (UP-31), revisar denuncias desde la app (UP-34), correo con el resultado de la moderación (UP-41), chat, calificaciones y notificaciones (Sprint 3).
