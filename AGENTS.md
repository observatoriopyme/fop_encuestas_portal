# AGENTS.md — Directrices de Desarrollo para Agentes de IA

Este documento define el estándar técnico y de comportamiento para agentes de IA
(Jules, Claude Code, etc.) que trabajen sobre el módulo `fop_encuestas_portal`
de la Fundación Observatorio PyME.

## 1. Contexto del Módulo

- **Propósito**: Exponer en el portal web de Odoo 17 los PDFs de encuestas
  completadas por cada usuario autenticado.
- **Fuente de datos**: Módulo `documents` (Enterprise). Carpeta `Encuestas`.
  Convención de nombre: `[login]@[ID].pdf`.
- **URLs expuestas**:
  - `/my/encuestas` — listado de encuestas del usuario
  - `/my/encuestas/<ID>.pdf` — PDF individual (inline, sin descarga forzada)
- **Entorno**: Odoo 17 Enterprise, multi-repo, rama `develop`.

## 2. Reglas de Oro

Antes de proponer cualquier cambio, el agente debe validar:

- **Sin hardcoding**: Nunca uses IDs fijos ni nombres de BD directamente.
  Usa referencias XML ID o búsquedas por campo `name`.
- **API de Odoo**: Usa exclusivamente la API `@api.model`, `@api.depends`,
  `@api.onchange` de Odoo 17. No uses APIs deprecadas de versiones anteriores.
- **sudo() con criterio**: `sudo()` está permitido únicamente en los métodos
  privados del controlador (`_get_encuestas_folder`, `_get_user_encuestas`).
  El control de acceso es responsabilidad del controlador (filtro por `=ilike`
  con el login del usuario). No amplíes el uso de `sudo()` a otros contextos
  sin justificación explícita.
- **Seguridad First**: Si se añaden modelos nuevos, agregar
  `security/ir.model.access.csv`. Este módulo no define modelos propios, pero
  si eso cambia la regla aplica inmediatamente.
- **No exponer adjuntos directos**: Los PDFs se sirven siempre a través de
  `ir.binary._get_stream_from`, nunca exponiendo IDs de `ir.attachment` en URLs.

## 3. Estructura del Módulo

```
fop_encuestas_portal/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── portal.py          # Extiende CustomerPortal
├── views/
│   └── portal_templates.xml
├── AGENTS.md
├── CHANGELOG.md
├── DESIGN.md
└── README.md
```

## 4. Convenciones de Código

### Python

- El controlador hereda de `odoo.addons.portal.controllers.portal.CustomerPortal`.
- Métodos privados con prefijo `_` (ej. `_get_user_encuestas`).
- Métodos de ruta decorados con `@http.route`.
- Usar `request.env.user.login` para identificar al usuario; nunca asumir
  que el login es case-sensitive (usar `=ilike` en dominios ORM).

### XML / QWeb

- Templates con `id` descriptivo, prefijados con `fop_encuestas_portal.`.
- Herencia de templates base de `portal` mediante `inherit_id`.
- Usar `t-out` (no `t-esc`) para output seguro en Odoo 17.
- Bootstrap 5: clases `btn-sm btn-primary`, `table table-hover`, `align-middle`.

## 5. Dependencias

| Módulo | Tipo | Nota |
|--------|------|------|
| `portal` | Community | Base del portal web |
| `website` | Community | Contexto website en rutas |
| `documents` | **Enterprise** | Fuente de los PDFs |

Si se agrega una dependencia nueva, actualizar `__manifest__.py` y este archivo.

## 6. Checklist Pre-commit para Agentes

- [ ] `__manifest__.py` sigue el formato `17.0.X.Y.Z` e incrementó el dígito correcto
- [ ] `__init__.py` importa todos los subdirectorios con módulos nuevos
- [ ] Ningún método nuevo usa `sudo()` sin justificación documentada
- [ ] Los templates XML usan `t-out` en lugar de `t-esc`
- [ ] No se introducen rutas sin `auth='user'` (este módulo no tiene rutas públicas)

## Actualización de CHANGELOG (obligatorio)

**Antes de cada commit**, agregar una entrada en `CHANGELOG.md` siguiendo el
formato y las reglas definidas en la **Sección 10 del AGENTS.md raíz** de `fop-odoo`.

No es un checkbox opcional: sin entrada en CHANGELOG no se completa el commit.
