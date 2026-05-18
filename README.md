# FOP Encuestas Portal

Addon de Odoo 17 que permite a los usuarios autenticados del website ver las encuestas que completaron, almacenadas como documentos PDF en el módulo Documents.

## Requisitos

- Odoo 17 Enterprise (requiere el módulo `documents`)
- Módulos: `portal`, `website`, `documents`

## Funcionamiento

Los documentos PDF de encuestas deben estar cargados en el módulo Documents:

- **Carpeta**: `Encuestas`
- **Nombre del archivo**: `[login_del_usuario]@[ID_de_la_encuesta].pdf`

  Ejemplo: `juan.perez@ENCUESTA-2024-001.pdf`

Cada usuario solo puede ver y descargar las encuestas cuyo nombre de archivo comienza con su login.
El control de acceso está basado en la convención de nombre de archivo.

## URLs

| URL | Descripción |
|-----|-------------|
| `/my/encuestas` | Listado de encuestas del usuario autenticado |
| `/my/encuestas/<ID>.pdf` | Descarga/visualización del PDF de la encuesta |

El botón "Encuestas" aparece en la sección "Mi" del portal (`/my`).

## Instalación

1. Copiar el addon al directorio de addons de Odoo.
2. Instalar desde el menú **Apps** buscando "FOP Encuestas Portal".

## Configuración

Crear en Documents una carpeta llamada exactamente `Encuestas` y subir los PDFs con el formato de nombre indicado.
