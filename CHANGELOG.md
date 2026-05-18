# CHANGELOG

Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.1.0/).
Versionado: `17.0.MAYOR.MENOR.PARCHE`.

Cada entrada de versión incluye el **prompt** que motivó los cambios,
para trazabilidad completa de las decisiones tomadas por agentes de IA.

---

## [17.0.1.1.0] — 2026-05-18

### Prompt

> Bien, ahora quiero que agregues al fop_encuestas_portal los archivos
> AGENTS.md, DESIGN.md y CHANGELOG.md; en el CHANGELOG.md me gustarías
> que aportes el Prompt que creó, cambió o eliminó código o documentación.

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
