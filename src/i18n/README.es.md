# Internacionalización (i18n)

Sistema de traducciones usando gettext (incluido en Python stdlib).

## Estructura

```
src/i18n/
├── __init__.py          # Módulo principal con función _()
├── compile.py           # Script para compilar .po → .mo
└── locales/
    ├── ckan_mcp.pot     # Template (source of truth)
    ├── es/LC_MESSAGES/
    │   ├── ckan_mcp.po  # Traducciones español
    │   └── ckan_mcp.mo  # Binario compilado
    └── en/LC_MESSAGES/
        ├── ckan_mcp.po  # Traducciones inglés
        └── ckan_mcp.mo  # Binario compilado
```

## Uso rápido

```python
from i18n import _

# En el código
message = _("CKAN Open Data Agent")
error = _("Found {} datasets").format(count)
```

```bash
# Configurar idioma
export CKAN_MCP_LANGUAGE=en  # inglés (default: es)

# Compilar traducciones después de editar .po
python src/i18n/compile.py
```

## Workflow de traducción

### 1. Extraer strings del código → Actualizar .pot

```bash
# Opción A: xgettext (si tienes gettext instalado)
xgettext -d ckan_mcp -o src/i18n/locales/ckan_mcp.pot src/*.py

# Opción B: pygettext (incluido en Python)
python -m pygettext -d ckan_mcp -o src/i18n/locales/ckan_mcp.pot src/*.py
```

### 2. Actualizar traducciones existentes

```bash
# Sincronizar .po con .pot (añade nuevos strings, marca obsoletos)
msgmerge -U src/i18n/locales/es/LC_MESSAGES/ckan_mcp.po src/i18n/locales/ckan_mcp.pot
msgmerge -U src/i18n/locales/en/LC_MESSAGES/ckan_mcp.po src/i18n/locales/ckan_mcp.pot
```

### 3. Editar traducciones

- Con editor de texto: editar `.po` manualmente
- Con GUI: usar [Poedit](https://poedit.net/), Lokalize, o Gtranslator

### 4. Compilar

```bash
python src/i18n/compile.py
```

## Añadir nuevo idioma

```bash
# Ejemplo: añadir francés
mkdir -p src/i18n/locales/fr/LC_MESSAGES
cp src/i18n/locales/ckan_mcp.pot src/i18n/locales/fr/LC_MESSAGES/ckan_mcp.po

# Editar header en el .po con información de francés
# Traducir los msgstr
# Compilar
python src/i18n/compile.py
```
