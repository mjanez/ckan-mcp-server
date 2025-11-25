# Internationalization (i18n)

Translation system using gettext (included in Python stdlib).

## Structure

```
src/i18n/
├── __init__.py          # Main module with _() function
├── compile.py           # Script to compile .po → .mo
└── locales/
    ├── ckan_mcp.pot     # Template (source of truth)
    ├── es/LC_MESSAGES/
    │   ├── ckan_mcp.po  # Spanish translations
    │   └── ckan_mcp.mo  # Compiled binary
    └── en/LC_MESSAGES/
        ├── ckan_mcp.po  # English translations
        └── ckan_mcp.mo  # Compiled binary
```

## Quick usage

```python
from i18n import _

# In the code
message = _("CKAN Open Data Agent")
error = _("Found {} datasets").format(count)
```

```bash
# Set language
export CKAN_MCP_LANGUAGE=en  # english (default: es)

# Compile translations after editing .po
python src/i18n/compile.py
```

## Translation workflow

### 1. Extract strings from code → Update .pot

```bash
# Option A: xgettext (if you have gettext installed)
xgettext -d ckan_mcp -o src/i18n/locales/ckan_mcp.pot src/*.py

# Option B: pygettext (included in Python)
python -m pygettext -d ckan_mcp -o src/i18n/locales/ckan_mcp.pot src/*.py
```

### 2. Update existing translations

```bash
# Sync .po with .pot (adds new strings, marks obsolete ones)
msgmerge -U src/i18n/locales/es/LC_MESSAGES/ckan_mcp.po src/i18n/locales/ckan_mcp.pot
msgmerge -U src/i18n/locales/en/LC_MESSAGES/ckan_mcp.po src/i18n/locales/ckan_mcp.pot
```

### 3. Edit translations

- With text editor: edit `.po` manually
- With GUI: use [Poedit](https://poedit.net/), Lokalize, or Gtranslator

### 4. Compile

```bash
python src/i18n/compile.py
```

## Add new language

```bash
# Example: add French
mkdir -p src/i18n/locales/fr/LC_MESSAGES
cp src/i18n/locales/ckan_mcp.pot src/i18n/locales/fr/LC_MESSAGES/ckan_mcp.po

# Edit header in .po with French information
# Translate the msgstr entries
# Compile
python src/i18n/compile.py
```

