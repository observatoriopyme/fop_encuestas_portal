# DESIGN.md — Decisiones de Diseño

## Objetivo

Permitir que usuarios autenticados del website de Odoo vean y accedan a los
PDFs de las encuestas que completaron, sin necesidad de acceso al backend ni
al módulo Documents.

---

## Arquitectura

### Fuente de datos: módulo Documents

Los PDFs de encuestas viven en el módulo `documents` (Enterprise) bajo la
carpeta `Encuestas`. Se eligió Documents porque:

- Es el repositorio centralizado de archivos del cliente.
- Permite al equipo de administración subir y gestionar los PDFs sin código.
- Soporta control de versiones de documentos de manera nativa.

No se crea ningún modelo propio en este addon. Toda la información se obtiene
consultando `documents.document` y `documents.folder`.

### Convención de nombre como control de acceso

El documento que le corresponde a un usuario se identifica por el nombre del
archivo siguiendo el patrón:

```
[login_del_usuario]@[ID_de_la_encuesta].pdf
```

Ejemplo: `juan.perez@ENCUESTA-2024-001.pdf`

**¿Por qué nombre de archivo y no `partner_id`?**

- El nombre es visible e inspeccionable sin acceder a la BD.
- Permite al equipo de administración subir PDFs y asignarlos simplemente
  nombrando el archivo, sin configurar relaciones ORM adicionales.
- El ID de la encuesta queda embebido en el nombre, facilitando trazabilidad.

El filtro ORM usa `=ilike` para tolerancia de mayúsculas/minúsculas en el login:

```python
('name', '=ilike', f'{user_login}@%.pdf')
```

### Controller: extensión de CustomerPortal

Se extiende `CustomerPortal` (patrón estándar de Odoo para el portal del cliente)
con tres métodos principales:

| Método | Propósito |
|--------|-----------|
| `_prepare_home_portal_values` | Provee `encuestas_count` para el contador asíncrono del home |
| `portal_my_encuestas` (GET /my/encuestas) | Renderiza la lista de encuestas del usuario |
| `portal_my_encuesta_pdf` (GET /my/encuestas/<ID>.pdf) | Sirve el PDF vía `ir.binary` |

### Servicio del PDF

Los archivos se sirven mediante `ir.binary._get_stream_from(document, field_name='raw')`,
el mecanismo estándar de Odoo 17 para streaming de binarios. Se eligió
`as_attachment=False` para que el PDF se abra en el navegador (inline) en lugar
de forzar la descarga.

El campo `raw` en `documents.document` es un campo relacionado con
`attachment_id.raw`, por lo que `ir.binary` accede directamente al store de
adjuntos sin exponer el ID del adjunto en la URL.

### URL del PDF

```
/my/encuestas/<survey_id>.pdf
```

El segmento `<survey_id>` es capturado por el converter `<string:survey_id>` de
werkzeug, que excluye slashes y es compatible con el `.pdf` literal en la ruta.

El `survey_id` en la URL corresponde a la parte del nombre del archivo
**después del `@` y antes de `.pdf`**. La construcción del nombre completo para
la búsqueda se hace en el controlador:

```python
doc_name = f'{user_login}@{survey_id}.pdf'
```

---

## Flujo de usuario

```
Usuario autenticado accede a /my
  → Ve el botón "Encuestas" con el contador (cargado async por /my/counters)
  → Hace click → /my/encuestas
    → Tabla con sus encuestas (survey_id + fecha)
    → Hace click en "Ver PDF" → /my/encuestas/<ID>.pdf
      → PDF abierto inline en el navegador
```

---

## Decisiones descartadas

| Alternativa | Motivo de descarte |
|-------------|-------------------|
| Usar `partner_id` en el documento | Requiere configuración extra al subir PDFs |
| Compartir vía `documents.share` (token público) | Innecesariamente complejo para usuarios ya autenticados |
| Redirigir a `/web/content/` con `access_token` | Expone el ID del adjunto y rompe la abstracción |
| Modelo propio con FK a `documents.document` | Añade complejidad sin beneficio para el caso de uso actual |

---

## Extensibilidad futura

- **Soporte a subcarpetas**: Si las encuestas se organizan en subcarpetas por
  año o tipo, ampliar `_get_encuestas_folder` para búsqueda recursiva con
  `child_of` en el dominio.
- **Filtro por `partner_id`**: Se puede combinar el filtro de nombre con un
  filtro por `partner_id` para mayor seguridad en entornos donde los logins
  puedan colisionar.
- **Paginación**: Si el volumen de encuestas por usuario crece, agregar
  `portal_pager` siguiendo el patrón estándar de Odoo.
