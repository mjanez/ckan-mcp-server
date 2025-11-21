"""
CKAN MCP Server - MCP Agent for CKAN open data portals.

This package provides a complete MCP (Model Context Protocol) server
to interact with CKAN portals intelligently.

Key features:
- Semantic search and advanced filtering
- SQL queries in DataStore
- Automatic detection of geospatial data
- Dynamic resources for metadata and schemas
- Response caching to optimize performance
- Automatic retry with exponential backoff

Basic usage:
    from client import get_client
    
    client = get_client()
    results = client.search_datasets("air quality")

To run the server:
    fastmcp run src/server.py
    
For development:
    fastmcp dev src/server.py

Author: mjanez
License: MIT
"""

__version__ = "1.0.0"
__author__ = "mjanez"
__license__ = "MIT"

from client import CKANClient, get_client

__all__ = ["CKANClient", "get_client"]
