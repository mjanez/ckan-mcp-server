# CKAN MCP Server
[![ES](https://img.shields.io/badge/lang-ES-yellow.svg)](README.es.md)
[![EN](https://img.shields.io/badge/lang-EN-blue.svg)](README.md)
[![FastMCP](https://img.shields.io/badge/FastMCP-v2.13%2B-blue?style=flat-square)](https://gofastmcp.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**Smart MCP Agent for CKAN Open Data Portals**

Semantic search, direct SQL queries, geospatial analysis, and advanced exploration of CKAN catalogs.

> [!TIP]
> **Recommended Test Portal**: `https://catalogo.datosabiertos.miteco.gob.es/catalogo`

## Key Features

  - Advanced semantic search with [SOLR filters](https://solr.apache.org/guide/6_6/common-query-parameters.html)
  - Automatic detection of geospatial datasets (`SHP`, `GeoJSON`, `WMS/WFS`, etc.)
  - SQL queries on [DataStore](https://docs.ckan.org/en/latest/maintaining/datastore.html) resources
  - Automatic inspection of portal schemas and capabilities
  - Data preview in Markdown table format
  - Smart caching and automatic retries for maximum stability
  - Full support for MCP resources (`ckan://...`)

## Quick Installation

```bash
git clone https://github.com/mjanez/ckan-mcp-server.git
cd ckan-mcp-server
uv venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
uv pip install -e .
```

### Optional Configuration (.env)

```env
CKAN_URL=https://catalogo.datosabiertos.miteco.gob.es/catalogo
CKAN_API_KEY=                  # Only if you need authenticated actions
LOG_LEVEL=INFO
```

## Usage

### Development Mode (with Web Inspector)

```bash
uv run fastmcp dev src/server.py
```

The MCP Inspector will automatically open in your browser to test all tools.

### Production Mode

```bash
uv run fastmcp run src/server.py
```

## Claude Desktop Integration

Add one or more servers to the Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "ckan-miteco": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/ckan-mcp-server", "run", "fastmcp", "run", "src/server.py"],
      "env": { "CKAN_URL": "https://catalogo.datosabiertos.miteco.gob.es/catalogo" }
    },
    "ckan-datosgob": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/ckan-mcp-server", "run", "fastmcp", "run", "src/server.py"],
      "env": { "CKAN_URL": "https://datos.gob.es" }
    }
  }
}
```

Configuration paths:

  - macOS/Linux: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Available Tools

| Tool | Description |
|---|---|
| `search_datasets` | Advanced search with filters (formats, organization, geospatial only, etc.) |
| `get_datasets` | Complete dataset information |
| `query_datastore` | SQL queries on tabular resources |
| `list_organizations` | List of organizations with dataset counts |
| `get_capabilities` | Detects active extensions (DataStore, Spatial, etc.) |

### MCP Resources

  - `ckan://dataset/{id}` → Complete dataset JSON
  - `ckan://dataset/{id}/schema` → DataStore Schemas
  - `ckan://info` → General portal information

## Usage Examples with Claude

  - `What datasets are available regarding air quality?`
  - `Search only for geospatial cadastre datasets`
  - `From resource 12345-abcd, execute: SELECT * FROM table WHERE year > 2020 LIMIT 20`
  - `Which organizations publish the most datasets?`

## Project
**Key Technologies**:

  - FastMCP v2.13+
  - ckanapi v4.7+
  - Pydantic v2
  - **gettext**
  - uv as package manager

### Internationalization

The project uses **gettext**:

```bash
# Configure language (default is Spanish)
export CKAN_MCP_LANGUAGE=en  # English
export CKAN_MCP_LANGUAGE=es  # Spanish

# Compile translations (only if you modify .po files)
python src/i18n/compile.py
```

See [src/i18n/README.md](https://www.google.com/search?q=src/i18n/README.md) for more details.

## Roadmap

  - Geospatial search by bounding box
  - Static map previews
  - Full DCAT-AP support and SPARQL queries
  - Automatic statistics on DataStore resources
  - Official Docker image
  - Tests + CI/CD

## License

MIT © mjanez – see [LICENSE](https://www.google.com/search?q=LICENSE)

## Acknowledgments

  - [FastMCP](https://gofastmcp.com) Team
  - [CKAN](https://github.com/ckan/ckan) project, [datos.gob.es](https://datos.gob.es/) and the Open Data Spain community

## Recommended CKAN Portals for Testing

  - [https://catalogo.datosabiertos.miteco.gob.es/catalogo](https://catalogo.datosabiertos.miteco.gob.es/catalogo)
  - [https://data.europa.eu](https://data.europa.eu)
  - [https://demo.ckan.org](https://demo.ckan.org)

-----

\<div align="center"\>
\<strong\>Find this useful?\</strong\> → \<a href="[https://github.com/mjanez/ckan-mcp-server](https://github.com/mjanez/ckan-mcp-server)"\>Leave a ⭐ on GitHub\!\</a\>
\</div\>