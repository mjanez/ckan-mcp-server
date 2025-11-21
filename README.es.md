# CKAN MCP Server
[![ES](https://img.shields.io/badge/lang-ES-yellow.svg)](README.es.md)
[![EN](https://img.shields.io/badge/lang-EN-blue.svg)](README.md)
[![FastMCP](https://img.shields.io/badge/FastMCP-v2.13%2B-blue?style=flat-square)](https://gofastmcp.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**Agente MCP inteligente para portales CKAN de datos abiertos**

Búsqueda semántica, consultas SQL directas, análisis geoespacial y exploración avanzada de catálogos CKAN.

> [!TIP]
> **Portal de prueba recomendado**: `https://catalogo.datosabiertos.miteco.gob.es/catalogo`

## Características principales

- Búsqueda semántica avanzada con [filtros SOLR](https://solr.apache.org/guide/6_6/common-query-parameters.html)
- Detección automática de datasets geoespaciales (`SHP`, `GeoJSON`, ` WMS/WFS`, etc.)
- Consultas SQL sobre recursos [DataStore](https://docs.ckan.org/en/latest/maintaining/datastore.html)
- Inspección automática de esquemas y capacidades del portal
- Previsualización de datos en formato tabla Markdown
- Caché inteligente y reintentos automáticos para máxima estabilidad
- Soporte completo para recursos MCP (`ckan://...`)

## Instalación rápida

```bash
git clone https://github.com/mjanez/ckan-mcp-server.git
cd ckan-mcp-server
uv venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
uv pip install -e .
```

### Configuración opcional (.env)

```env
CKAN_URL=https://catalogo.datosabiertos.miteco.gob.es/catalogo
CKAN_API_KEY=                  # Solo si necesitas acciones autenticadas
LOG_LEVEL=INFO
```

## Ejecución

### Modo desarrollo (con Inspector web)

```bash
uv run fastmcp dev src/server.py
```

Se abrirá automáticamente el MCP Inspector en tu navegador para probar todas las herramientas.

### Modo producción

```bash
uv run fastmcp run src/server.py
```

## Integración con Claude Desktop

Añade uno o varios servidores al archivo de configuración de Claude Desktop:

```json
{
  "mcpServers": {
    "ckan-miteco": {
      "command": "uv",
      "args": ["--directory", "/ruta/absoluta/ckan-mcp-server", "run", "fastmcp", "run", "src/server.py"],
      "env": { "CKAN_URL": "https://catalogo.datosabiertos.miteco.gob.es/catalogo" }
    },
    "ckan-datosgob": {
      "command": "uv",
      "args": ["--directory", "/ruta/absoluta/ckan-mcp-server", "run", "fastmcp", "run", "src/server.py"],
      "env": { "CKAN_URL": "https://datos.gob.es" }
    }
  }
}
```

Rutas de configuración:
- macOS/Linux: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Herramientas disponibles

| Herramienta               | Descripción                                           |
|---------------------------|-------------------------------------------------------|
| `search_datasets`         | Búsqueda avanzada con filtros (formatos, organización, solo geoespaciales, etc.) |
| `get_datasets`         | Información completa de un dataset                    |
| `query_datastore`     | Consultas SQL sobre recursos tabulares                |
| `list_organizations`   | Listado de organizaciones con conteo de datasets      |
| `get_capabilities`    | Detecta extensiones activas (DataStore, Spatial, etc.) |

### Recursos MCP

- `ckan://dataset/{id}` → JSON completo del dataset
- `ckan://dataset/{id}/schema` → Esquemas DataStore
- `ckan://info` → Información general del portal

## Ejemplos de uso con Claude

- `¿Qué datasets hay sobre calidad del aire?`
- `Busca solo datasets geoespaciales de catastro`
- `Del recurso 12345-abcd, ejecuta: SELECT * FROM tabla WHERE año > 2020 LIMIT 20`
- `¿Qué organizaciones publican más datasets?`

## Proyecto
**Tecnologías principales**:
- FastMCP v2.13+
- ckanapi v4.7+
- Pydantic v2
- **gettext**
- uv como gestor de paquetes

### Internacionalización

El proyecto usa **gettext**:

```bash
# Configurar idioma (español por defecto)
export CKAN_MCP_LANGUAGE=en  # inglés
export CKAN_MCP_LANGUAGE=es  # español

# Compilar traducciones (solo si modificas .po)
python src/i18n/compile.py
```

Ver [src/i18n/README.md](src/i18n/README.md) para más detalles.

## Roadmap

- Búsqueda geoespacial por bounding box
- Previews de mapas estáticos
- Soporte completo DCAT-AP y consultas SPARQL
- Estadísticas automáticas sobre recursos DataStore
- Imagen Docker oficial
- Tests + CI/CD

## Licencia

MIT © mjanez – ver [LICENSE](LICENSE)

## Agradecimientos

- Equipo de [FastMCP](https://gofastmcp.com)
- Proyecto [CKAN](https://github.com/ckan/ckan), [datos.gob.es](https://datos.gob.es/) y la comunidad Open Data España

## Portales CKAN recomendados para pruebas

- https://catalogo.datosabiertos.miteco.gob.es/catalogo
- https://data.europa.eu
- https://demo.ckan.org

---

<div align="center">
  <strong>¿Te resulta útil?</strong> → <a href="https://github.com/mjanez/ckan-mcp-server">¡Deja una ⭐ en GitHub!</a>
</div>