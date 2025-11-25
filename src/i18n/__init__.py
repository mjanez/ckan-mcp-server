"""Internationalization module for CKAN MCP Server using gettext."""

import gettext
import os
from pathlib import Path

LOCALE_DIR = Path(__file__).parent / "locales"
DOMAIN = "ckan_mcp"

_state = {
    "language": os.getenv("CKAN_MCP_LANGUAGE", "es"),
    "translation": None,
}

_state["translation"] = gettext.translation(
    DOMAIN,
    localedir=str(LOCALE_DIR),
    languages=[_state["language"]],
    fallback=True
)

_ = _state["translation"].gettext


def get_translation(lang: str = None):
    """Get gettext translation function for specified language.

    Args:
        lang: Language code ('es' or 'en'). Defaults to current language

    Returns:
        Translation function
    """
    if lang is None:
        lang = _state["language"]

    try:
        trans = gettext.translation(
            DOMAIN,
            localedir=str(LOCALE_DIR),
            languages=[lang],
            fallback=True
        )
        return trans.gettext
    except (OSError, ValueError):
        return _state["translation"].gettext


def set_language(lang: str) -> None:
    """Set language for translations.

    Args:
        lang: Language code ('es' or 'en')
    """
    _state["language"] = lang
    _state["translation"] = gettext.translation(
        DOMAIN,
        localedir=str(LOCALE_DIR),
        languages=[lang],
        fallback=True
    )


def get_language() -> str:
    """Get current configured language.

    Returns:
        Language code ('es' or 'en')
    """
    return _state["language"]
