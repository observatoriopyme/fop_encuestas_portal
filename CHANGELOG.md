# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado: `17.0.MAYOR.MENOR.PARCHE`.

Cada entrada de versión incluye el **prompt** que motivó los cambios
y las **discusiones de diseño** relevantes que influyeron en las decisiones,
para trazabilidad completa del razonamiento de agentes de IA.

---

## [17.0.1.0.1] — 2026-07-16

### Modificado

- `AGENTS.md`: referencia a la sección del AGENTS.md raíz de `fop-odoo` corregida
  (Sección 17 -> Sección 10), tras la reestructuración de ese documento.

---

## [17.0.1.2.0] — 2026-05-18

### Prompt

> En el CHANGELOG.md también cualquier discusión que se hayan tenido en cuenta
> para el diseño y la implementación. Agrega esta regla al AGENTS.md para que
> no se tenga que recordar estos cambios en el CHANGELOG.md en los próximos
> cambios.

### Discusión de diseño

- Se retroalimenta el `CHANGELOG.md` de las versiones `17.0.1.0.0` y
  `17.0.1.1.0` con las discusiones de diseño que existieron pero no fueron
  registradas inicialmente.
- Se agrega al checklist del `AGENTS.md` la obligación explícita de documentar
  discusiones de diseño (no solo el prompt) en cada entrada del changelog.
- Se eligió mantener las discusiones **inline en el CHANGELOG** (en lugar de
  solo en `DESIGN.md`) para que quede completa la trazabilidad temporal:
  el `DESIGN.md` describe el estado actual del diseño, el `CHANGELOG.md`
  describe la evolución y el razonamiento paso a paso.

### Modificado

- `CHANGELOG.md`: encabezado actualizado para indicar que cada versión incluye
  prompt y discusiones de diseño. Versiones anteriores enriquecidas con
  secciones `### Discusión de diseño`.
- `AGENTS.md`: ítem del checklist pre-commit extendido para requerir también
  el registro de discusiones de diseño relevantes.

---

## [17.0.1.1.0] — 2026-05-18

### Prompt

> Bien, ahora quiero que agregues al fop_encuestas_portal los archivos
> AGENTS.md, DESIGN.md y CHANGELOG.md; en el CHANGELOG.md me gustarías
> que aportes el Prompt que creó, cambió o eliminó código o documentación.

### Discusión de diseño

- **Formato del CHANGELOG**: se adoptó [Keep a Changelog](https://keepachangelog.com/es/1.1.0/)
  como referencia por ser un estándar conocido. Se decidió incluir el prompt
  completo (no solo un resumen) para que un agente que retome el trabajo en el
  futuro pueda reconstruir la intención del usuario sin ambigüedades.
- **Formato del AGENTS.md**: se tomó como base el `AGENTS.md` del addon
  `fop_odoo_theme` que ya existe en el proyecto, adaptando las reglas al
  contexto específico de este módulo (controllers vs models, uso de `sudo()`
  en portal, etc.).
- **DESIGN.md vs CHANGELOG.md**: se decidió separar las decisiones de diseño
  en `DESIGN.md` (estado actual del diseño, atemporal) del `CHANGELOG.md`
  (evolución y razonamiento por versión). Ambos documentos son complementarios.

### Añadido

- `AGENTS.md`: directrices de desarrollo para agentes de IA (Jules, Claude Code).
  Define reglas de uso de `sudo()`, convenciones de código Python/XML,
  estructura del módulo y checklist pre-commit.
- `DESIGN.md`: documentación de decisiones de diseño. Explica la arquitectura,
  el flujo de usuario, por qué se usa la convención de nombre de archivo como
  control de acceso, cómo se sirven los PDFs vía `ir.binary`, y alternativas
  descartadas.
- `CHANGELOG.md`: este archivo. Registra cambios por versión junto al prompt
  que los originó.

---

## [17.0.1.0.0] — 2026-05-18

### Prompt

> Crea un nuevo addon de Odoo para que los usuarios del website que estén
> autenticados puedan ver las encuestas que completaron. Las encuestas van a
> estar cargadas en el addon Documents, un documento PDF, en la carpeta
> encuestas. Los usuarios solo van a poder ver las encuestas que respondieron
> y no otras, y ese control indicando que el documento es compartido con ellos.
>
> La URL para acceder va a ser /my/encuestas : ahí se ven todos los documentos.
> Y para acceder al documento va a ser /my/encuestas/[ID de la encuesta].pdf
> que el ID va a ser el nombre del archivo. Se espera que el nombre del
> documento en Documents, tiene que estar en la carpeta /Encuestas y el nombre
> del PDF debería ser [login]@[ID de la encuesta].pdf.
>
> Para acceder a esa página implementar un botón de My específico.
>
> Crea el addon, subilo como repositorio de la organización observatoriopyme
> y que quede como submodulo de fop-odoo.

### Discusión de diseño

**Control de acceso: nombre de archivo vs `partner_id`**

Se evaluaron tres mecanismos para determinar qué documentos pertenecen a cada
usuario:

1. `partner_id` en `documents.document` → requiere configurar la relación al
   subir cada PDF; suma fricción operativa sin ventaja técnica en este caso.
2. `documents.share` con tokens → diseñado para compartir con usuarios no
   autenticados; innecesariamente complejo cuando el usuario ya tiene sesión.
3. **Convención de nombre `[login]@[ID].pdf`** ← elegida. El nombre es
   inspeccionable sin acceder a la BD, el equipo de administración solo
   necesita nombrar el archivo correctamente, y el ID de la encuesta queda
   embebido para trazabilidad.

**`=ilike` en el dominio ORM**

Se usó `('name', '=ilike', f'{user_login}@%.pdf')` en lugar de `=like` para
tolerar diferencias de mayúsculas/minúsculas en el login (Odoo admite logins
tipo email, que a veces se ingresan con capitalización inconsistente).

**Servicio del PDF: `ir.binary` vs `/web/content/`**

Redirigir a `/web/content/<attachment_id>/...` habría expuesto el ID interno
del adjunto en la URL, permitiendo a un usuario manipularla para intentar
acceder a otros adjuntos. Se eligió `ir.binary._get_stream_from(document, 'raw')`
porque es el patrón estándar del propio módulo Documents y no expone IDs
internos.

Se usó `as_attachment=False` para que el navegador muestre el PDF inline en
lugar de forzar la descarga, mejorando la experiencia del usuario.

**Ruta URL: `<string:survey_id>.pdf` vs `<path:filename>`**

`<path:filename>` permite slashes en el segmento, lo que añade superficie de
ataque innecesaria. `<string:survey_id>.pdf` con el sufijo `.pdf` literal es
manejado correctamente por werkzeug y restringe el parámetro a un identificador
sin slashes.

**`portal_client_category_enable = True` incondicional**

Se consideró condicionar la visibilidad del botón "Encuestas" a que
`encuestas_count > 0`. Se descartó porque: (a) el contador se carga
asincrónicamente y no está disponible en el render inicial, y (b) mostrar
la sección aunque esté vacía es coherente con cómo Odoo muestra otras
secciones del portal (Pedidos, Facturas, etc.).

**`sudo()` acotado a métodos privados**

El `sudo()` se usa solo en `_get_encuestas_folder` y `_get_user_encuestas`.
El control de acceso real lo impone el filtro de nombre antes de servir
cualquier dato. Los métodos de ruta (`@http.route`) no usan `sudo()` directamente.

**`documents.document` vs `ir.attachment` en `ir.binary`**

Se pasó `documents.document` (no `ir.attachment`) a `ir.binary._get_stream_from`
con `field_name='raw'`, que es un campo relacionado con `attachment_id.raw`.
Esto replica exactamente el patrón del controlador del propio módulo Documents
y evita exponer el ID del adjunto.

### Añadido

- `__manifest__.py`: manifiesto del addon. Depende de `portal`, `website`,
  `documents`. Versión `17.0.1.0.0`, licencia OPL-1.
- `__init__.py`: importa el paquete `controllers`.
- `controllers/__init__.py`: importa el módulo `portal`.
- `controllers/portal.py`: controlador `EncuestasPortal` que extiende
  `CustomerPortal`. Implementa:
  - `_prepare_home_portal_values`: provee el contador `encuestas_count`
    para el botón asíncrono del portal home.
  - `_get_encuestas_folder`: busca la carpeta `Encuestas` en `documents.folder`.
  - `_get_user_encuestas`: filtra documentos con `=ilike '{login}@%.pdf'`
    en la carpeta `Encuestas`.
  - `_parse_survey_id`: extrae el ID de la encuesta del nombre del archivo.
  - `GET /my/encuestas`: renderiza el listado de encuestas del usuario.
  - `GET /my/encuestas/<survey_id>.pdf`: sirve el PDF inline vía
    `ir.binary._get_stream_from`.
- `views/portal_templates.xml`: dos templates QWeb:
  - `portal_my_home_menu_encuestas`: inyecta el botón "Encuestas" en el
    home del portal (`/my`) con contador asíncrono.
  - `portal_my_encuestas`: tabla de encuestas con columnas Survey ID, Fecha
    y enlace "Ver PDF".
- `README.md`: documentación de instalación y uso del addon.
- `.gitignore`: excluye `__pycache__/` y `.pyc`.

### Infraestructura

- Repositorio creado en `https://github.com/observatoriopyme/fop_encuestas_portal`
  (rama `develop`).
- Agregado como submódulo en `fop-odoo` en la ruta `addons/fop_encuestas_portal`.
