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

### Control de acceso: `ir.rule` por `partner_id` (reemplaza la convención de nombre)

> **Nota histórica**: la versión original de este addon (hasta `17.0.1.2.0`)
> usaba una convención de nombre de archivo (`[login]@[ID].pdf`) filtrada con
> `=ilike` en el controlador. Ese mecanismo fue reemplazado en el refactor de
> mayo de 2026 (ver CHANGELOG `17.0.1.3.0`) por una regla de registro (`ir.rule`)
> sobre `documents.document`, que es la alternativa que originalmente se había
> descartado (ver tabla más abajo). El razonamiento puntual de ese cambio no
> quedó registrado en su momento; esta sección documenta el estado **actual**.

El acceso ya no depende del nombre del archivo. Se define en
`security/document_user_rule.xml` una regla de registro para el grupo
`base.group_portal`:

```xml
<record id="rule_documents_portal_own_only" model="ir.rule">
    <field name="model_id" ref="documents.model_documents_document"/>
    <field name="domain_force">[('partner_id', '=', user.partner_id.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="False"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

Esto significa que:

- El control de acceso lo impone el ORM automáticamente en cualquier `search()`
  no-`sudo()` sobre `documents.document` hecho por un usuario portal.
- Para que un documento sea visible, el equipo de administración debe asignarle
  el `partner_id` del usuario correspondiente al subirlo (ya no basta con
  nombrar el archivo).
- Se agrega `security/ir.model.access.csv` otorgando `perm_read` sobre
  `documents.document` al grupo `base.group_portal` (sin este ACL de modelo,
  la `ir.rule` no tendría efecto).

### Carpeta de encuestas: búsqueda bilingüe

`_get_surveys_folder` busca la carpeta por nombre en `es_AR` (`Encuestas`) y
`en_US` (`Surveys`), en ese orden, usando `=ilike` y `with_context(lang=...)`
para tolerar el idioma de instalación de la base. El listado de documentos
(`_get_user_surveys`) ya **no filtra por nombre de archivo** — devuelve todos
los documentos de la carpeta que la `ir.rule` deja ver al usuario.

### Controller: extensión de CustomerPortal

Se extiende `CustomerPortal` (patrón estándar de Odoo para el portal del cliente)
con los siguientes métodos principales:

| Método | Propósito |
|--------|-----------|
| `_prepare_home_portal_values` | Provee `surveys_count` para el contador asíncrono del home |
| `_get_surveys_folder` | Busca la carpeta `Encuestas`/`Surveys` (bilingüe, `sudo()`) |
| `_get_user_surveys` | Lista documentos de la carpeta, filtrados por la `ir.rule` (sin `sudo()`) |
| `portal_my_encuestas` (GET /my/encuestas) | Renderiza la lista de encuestas del usuario |
| `portal_my_survey_pdf` (GET /my/encuestas/<access_token>) | Sirve el PDF vía `ir.binary`, buscando el documento por `access_token` (`sudo()`) |

### Servicio del PDF

Los archivos se sirven mediante `ir.binary._get_stream_from(document, field_name='raw')`,
el mecanismo estándar de Odoo 17 para streaming de binarios. Se eligió
`as_attachment=False` para que el PDF se abra en el navegador (inline) en lugar
de forzar la descarga.

El campo `raw` en `documents.document` es un campo relacionado con
`attachment_id.raw`, por lo que `ir.binary` accede directamente al store de
adjuntos sin exponer el ID del adjunto en la URL.

### URL del PDF: `access_token` (reemplaza `survey_id`)

```
/my/encuestas/<access_token>
```

El segmento ya **no** es un `survey_id` derivado del nombre del archivo ni
lleva el sufijo `.pdf`: es el `access_token` estándar de Odoo
(`attachment_id.generate_access_token()`), generado al listar las encuestas
del usuario y usado por el controlador para localizar el documento vía
`sudo()` sin depender de la `ir.rule`. Esto mantiene la propiedad de no
exponer IDs internos en la URL, ahora sin necesidad de la convención de nombre.

---

## Flujo de usuario

```
Usuario autenticado accede a /my
  → Ve el botón "Encuestas" con el contador (cargado async por /my/counters)
  → Hace click → /my/encuestas
    → Tabla con sus encuestas (etiqueta "Encuesta #N" + fecha)
    → Hace click en "Ver PDF" → /my/encuestas/<access_token>
      → PDF abierto inline en el navegador
```

---

## Decisiones descartadas (histórico)

> Esta tabla refleja el análisis de la versión original (`17.0.1.0.0`). El
> refactor de `17.0.1.3.0` adoptó `partner_id` en `ir.rule` como mecanismo de
> acceso real (ver sección más arriba); se conserva la tabla como registro
> histórico del razonamiento inicial.

| Alternativa | Motivo de descarte (análisis original) | Estado actual |
|-------------|-------------------|---------------|
| Usar `partner_id` en el documento | Requiere configuración extra al subir PDFs | **Adoptada** desde `17.0.1.3.0` vía `ir.rule` |
| Compartir vía `documents.share` (token público) | Innecesariamente complejo para usuarios ya autenticados | Descartada, sigue vigente |
| Redirigir a `/web/content/` con `access_token` | Expone el ID del adjunto y rompe la abstracción | Descartada; el `access_token` se usa solo como parámetro de búsqueda, no como URL de `/web/content/` |
| Modelo propio con FK a `documents.document` | Añade complejidad sin beneficio para el caso de uso actual | Descartada, sigue vigente |

---

## Extensibilidad futura

- **Soporte a subcarpetas**: Si las encuestas se organizan en subcarpetas por
  año o tipo, ampliar `_get_surveys_folder` para búsqueda recursiva con
  `child_of` en el dominio.
- **Paginación**: Si el volumen de encuestas por usuario crece, agregar
  `portal_pager` siguiendo el patrón estándar de Odoo.
- **Traducciones frontend**: `models/ir_http.py` extiende
  `_get_translation_frontend_modules_name`; revisar si el módulo agregado
  (`fop_dashboard_coyuntural`) es intencional o un arrastre de otro addon,
  ya que no guarda relación evidente con encuestas/portal.
