# FOP Encuestas Portal

Addon de Odoo 17 que permite a los usuarios autenticados del website ver las encuestas que completaron, almacenadas como documentos PDF en el módulo Documents.

## Requisitos

- Odoo 17 Enterprise (requiere el módulo `documents`)
- Módulos: `portal`, `website`, `documents`

## Funcionamiento

Los documentos PDF de encuestas deben estar cargados en el módulo Documents:

- **Carpeta**: `Encuestas` (idioma `es_AR`) o `Surveys` (idioma `en_US`).
- **`partner_id` del documento**: debe apuntar al contacto del usuario portal
  que debe poder verlo. El control de acceso se basa en esto (regla de
  registro `ir.rule` sobre `documents.document`, no en el nombre del archivo).

Cada usuario portal solo puede ver los documentos de esa carpeta cuyo
`partner_id` coincide con su propio contacto.

## URLs

| URL | Descripción |
|-----|-------------|
| `/my/encuestas` | Listado de encuestas del usuario autenticado |
| `/my/encuestas/<access_token>` | Visualización inline del PDF de una encuesta (el link se genera automáticamente desde el listado) |

El botón "Encuestas" aparece en la sección "Mi" del portal (`/my`).

## Instalación

1. Copiar el addon al directorio de addons de Odoo.
2. Instalar desde el menú **Apps** buscando "FOP Encuestas Portal".

## Configuración

Crear en Documents una carpeta llamada `Encuestas` (o `Surveys`) y subir los
PDFs asignando el `partner_id` del contacto correspondiente a cada documento.
