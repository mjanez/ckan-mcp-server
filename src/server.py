"""CKAN MCP Server - Intelligent agent for CKAN open data portals.

This MCP server provides advanced access to CKAN portals with:
- Semantic search and advanced filtering
- Schema inspection and SQL queries
- Geospatial data detection and handling
- Dynamic resources for metadata, RDF/DCAT, and schemas
- Response caching for optimized performance
"""

from fastmcp import FastMCP, Context
from fastmcp.server.middleware.caching import ResponseCachingMiddleware
from typing import Optional, List, Dict, Any
from pydantic import Field
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from client import CKANClient, get_client
from i18n import _

logger = logging.getLogger(__name__)

mcp = FastMCP("CKAN Open Data Agent")
mcp.add_middleware(ResponseCachingMiddleware())

logger.info(_("CKAN MCP server initialized"))


@mcp.tool(
    description=_("Search datasets in CKAN catalog with advanced filters and geospatial detection")
)
async def search_datasets(
    query: str = Field(
        default="*:*",
        description=_("SOLR search terms (e.g., 'air quality', 'cadastre', or '*:*' for all)")
    ),
    formats: List[str] = Field(
        default_factory=list,
        description=_("Filter by resource formats (e.g., ['CSV', 'SHP', 'GeoJSON'])")
    ),
    organization: Optional[str] = Field(
        default=None,
        description=_("Filter by organization name")
    ),
    only_geospatial: bool = Field(
        default=False,
        description=_("Show only datasets with geospatial data (SHP, KML, GeoJSON, WMS, etc.)")
    ),
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description=_("Maximum number of results (1-100)")
    ),
    ctx: Context = None
) -> str:
    """Search datasets in CKAN catalog.

    Features:
    - Fuzzy search and field-specific queries
    - Resource format filtering
    - Automatic geospatial data detection
    - Visual icons (🌍 for geo, 📦 for others)
    """
    client = get_client()

    if ctx:
        await ctx.info(_("Querying {}").format(client.url) + "...")
        await ctx.report_progress(10, 100)

    try:
        filters = {}
        if formats:
            filters['res_format'] = [f.upper() for f in formats]
        if organization:
            filters['organization'] = organization

        results = client.search_datasets(
            query=query,
            filters=filters if filters else None,
            rows=limit
        )

        if ctx:
            await ctx.report_progress(80, 100)

        count = results['count']
        packages = results['results']

        if count == 0:
            return _("No datasets found. Try more general terms or remove filters.")

        if only_geospatial:
            packages = [pkg for pkg in packages if client.is_geospatial_dataset(pkg)]
            if not packages:
                return _("No geospatial datasets found with those criteria.")

        output = [_("Found {} datasets (showing {})").format(count, len(packages)) + ":\n"]

        for i, pkg in enumerate(packages, 1):
            is_geo = client.is_geospatial_dataset(pkg)
            icon = "🌍" if is_geo else "📦"

            org = pkg.get('organization') or {}
            org_title = org.get('title', _("No organization"))

            resources_info = []
            for r in pkg.get('resources', []):
                fmt = r.get('format', 'N/A')
                resources_info.append(fmt)

            output.append(f"### {i}. {icon} {pkg['title']}")
            output.append(f"   - **{_('ID')}**: `{pkg['id']}`")
            output.append(f"   - **{_('Organization')}**: {org_title}")
            output.append(f"   - **{_('Resources')}**: {', '.join(resources_info) if resources_info else _('None')}")

            if is_geo:
                geo_resources = client.get_geospatial_resources(pkg)
                geo_formats = [r['format'] for r in geo_resources]
                output.append(f"   - **{_('Geo formats')}**: {', '.join(geo_formats)}")

            output.append(f"   - **{_('Inspect')}**: `ckan://dataset/{pkg['id']}`\n")

        if ctx:
            await ctx.report_progress(100, 100)
            await ctx.info(_("Search completed: {} results").format(len(packages)))

        return "\n".join(output)

    except Exception as e:
        error_msg = _("Error searching datasets: {}").format(str(e))
        if ctx:
            await ctx.error(error_msg)
        return error_msg


@mcp.tool(
    description=_("Get detailed information for a specific dataset including metadata and resources")
)
async def get_datasets(
    dataset_id: str = Field(
        description=_("Dataset ID or name (slug)")
    ),
    ctx: Context = None
) -> str:
    """Get complete information for a dataset.

    Args:
        dataset_id: Dataset ID or slug name
        ctx: Optional FastMCP context for progress reporting

    Returns:
        Formatted dataset information with metadata and resources
    """
    client = get_client()

    if ctx:
        await ctx.info(_("Getting dataset {}").format(dataset_id) + "...")

    try:
        dataset = client.get_dataset(dataset_id)

        is_geo = client.is_geospatial_dataset(dataset)
        icon = "🌍" if is_geo else "📦"

        output = [f"# {icon} {dataset.get('title', _('No title'))}"]
        output.append(f"\n**{_('ID')}**: `{dataset['id']}`")
        output.append(f"**{_('Name')}**: `{dataset.get('name', 'N/A')}`")

        org = dataset.get('organization')
        if org:
            output.append(f"**{_('Organization')}**: {org.get('title', 'N/A')}")

        notes = dataset.get('notes', '').strip()
        if notes:
            output.append(f"\n## {_('Description')}\n{notes}")

        license_title = dataset.get('license_title', _('Not specified'))
        output.append(f"\n**{_('License')}**: {license_title}")

        resources = dataset.get('resources', [])
        output.append(f"\n## 📎 {_('Resources')} ({len(resources)})")

        for i, res in enumerate(resources, 1):
            res_format = res.get('format', 'N/A')
            is_geo_format = res_format.lower() in {'shp', 'kml', 'geojson', 'wms', 'wfs', 'gpkg'}
            res_icon = "🗺️" if is_geo_format else "📄"

            output.append(f"\n### {i}. {res_icon} {res.get('name', _('No name'))}")
            output.append(f"   - **{_('ID')}**: `{res['id']}`")
            output.append(f"   - **{_('Format')}**: {res_format}")
            output.append(f"   - **URL**: {res.get('url', 'N/A')}")

            if client.has_datastore(res['id']):
                output.append(f"   - **{_('DataStore active')}** ({_('SQL queries available')})")
                output.append(f"   - {_('Use')}: `query_datastore(resource_id=\"{res['id']}\")`")

        if ctx:
            await ctx.info(_("Dataset retrieved successfully"))

        return "\n".join(output)

    except Exception as e:
        error_msg = _("Error retrieving dataset: {}").format(str(e))
        if ctx:
            await ctx.error(error_msg)
        return error_msg


@mcp.tool(
    description=_("Query DataStore resource content or execute custom SQL")
)
async def query_datastore(
    resource_id: str = Field(
        description=_("Resource ID to query")
    ),
    sql_query: Optional[str] = Field(
        default=None,
        description=_("Custom SQL query (if not provided, shows first rows)")
    ),
    limit: int = Field(
        default=10,
        ge=1,
        le=1000,
        description=_("Maximum number of rows to return")
    ),
    ctx: Context = None
) -> str:
    """Query data in CKAN DataStore.

    Args:
        resource_id: Resource ID to query
        sql_query: Optional custom SQL query
        limit: Maximum number of rows to return
        ctx: Optional FastMCP context for progress reporting

    Returns:
        Formatted query results as Markdown table
    """
    client = get_client()

    if ctx:
        await ctx.info("🔍 " + _("Querying DataStore for resource {}").format(resource_id) + "...")

    try:
        if not client.has_datastore(resource_id):
            return (
                _("Resource `{}` does not have active DataStore.").format(resource_id) + "\n" +
                _("This can happen if it is a PDF, ZIP, or other non-tabular format.")
            )

        schema = client.get_datastore_schema(resource_id)

        if sql_query:
            result = client.datastore_search_sql(sql_query)
            records = result.get('records', [])
        else:
            result = client.datastore_search(resource_id=resource_id, limit=limit)
            records = result.get('records', [])

        if not records:
            return _("No records found.")

        output = [_("Results ({} rows)").format(len(records)) + ":\n"]

        if records:
            headers = list(records[0].keys())
            output.append("| " + " | ".join(headers) + " |")
            output.append("| " + " | ".join(["---"] * len(headers)) + " |")

            for record in records[:limit]:
                row = []
                for header in headers:
                    value = str(record.get(header, ''))
                    if len(value) > 50:
                        value = value[:47] + "..."
                    row.append(value)
                output.append("| " + " | ".join(row) + " |")

        if ctx:
            await ctx.info(_("Query completed: {} rows").format(len(records)))

        return "\n".join(output)

    except Exception as e:
        error_msg = _("Error querying DataStore: {}").format(str(e))
        if ctx:
            await ctx.error(error_msg)
        return error_msg


@mcp.tool(
    description=_("List available organizations in CKAN portal")
)
async def list_organizations(
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description=_("Maximum number of organizations")
    ),
    ctx: Context = None
) -> str:
    """List portal organizations with dataset counts.

    Args:
        limit: Maximum number of organizations to return
        ctx: Optional FastMCP context for progress reporting

    Returns:
        Formatted list of organizations with dataset counts
    """
    client = get_client()

    if ctx:
        await ctx.info(_("Getting list of organizations..."))

    try:
        orgs = client.action.organization_list(all_fields=True, limit=limit)

        if not orgs:
            return _("No organizations found.")

        output = [_("Found {} organizations").format(len(orgs)) + ":\n"]

        for i, org in enumerate(orgs, 1):
            pkg_count = org.get('package_count', 0)
            output.append(
                f"{i}. **{org.get('title', org.get('name', 'N/A'))}** "
                f"({pkg_count} {_('datasets')})\n"
                f"   - {_('ID')}: `{org['id']}`"
            )

        return "\n".join(output)

    except Exception as e:
        error_msg = _("Error listing organizations: {}").format(str(e))
        if ctx:
            await ctx.error(error_msg)
        return error_msg


@mcp.tool(
    description=_("Detect CKAN portal capabilities and extensions")
)
async def get_capabilities(ctx: Context = None) -> str:
    """Detect CKAN portal capabilities and features.

    Args:
        ctx: Optional FastMCP context for progress reporting

    Returns:
        Formatted report of portal capabilities and extensions
    """
    client = get_client()

    if ctx:
        await ctx.info(_("Analyzing portal capabilities..."))

    try:
        capabilities = client.check_capabilities()
        site_info = client.get_site_info()

        output = [f"# {_('Capabilities of')} {client.url}\n"]

        ckan_version = site_info.get('ckan_version', _('Unknown'))
        output.append(f"**{_('CKAN Version')}**: {ckan_version}\n")

        output.append(f"## {_('Detected extensions')}:")

        cap_icons = {
            'datastore': ('🗄️', _('DataStore (SQL queries on resources)')),
            'spatial': ('🗺️', _('Spatial (geospatial searches)')),
            'dcat': ('📋', _('DCAT (RDF/JSON-LD metadata)')),
            'harvest': ('🌾', _('Harvest (metadata collection)')),
            'datapusher': ('⬆️', _('DataPusher (automatic DataStore loading)'))
        }

        for cap, enabled in capabilities.items():
            icon, desc = cap_icons.get(cap, ('❓', cap))
            status = _('Active') if enabled else _('Not available')
            output.append(f"- {icon} **{desc}**: {status}")

        if ctx:
            await ctx.info(_("Analysis completed"))

        return "\n".join(output)

    except Exception as e:
        error_msg = _("Error detecting capabilities: {}").format(str(e))
        if ctx:
            await ctx.error(error_msg)
        return error_msg


@mcp.resource("ckan://dataset/{dataset_id}")
def resource_dataset_json(dataset_id: str) -> str:
    """Return complete dataset metadata as JSON.

    Args:
        dataset_id: Dataset ID or slug

    Returns:
        JSON string containing full dataset metadata
    """
    client = get_client()
    try:
        dataset = client.get_dataset(dataset_id)
        return json.dumps(dataset, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.resource("ckan://dataset/{dataset_id}/schema")
def resource_datastore_schemas(dataset_id: str) -> str:
    """Return DataStore schemas for all resources in a dataset.

    Args:
        dataset_id: Dataset ID or slug

    Returns:
        JSON string containing schemas for all DataStore-enabled resources
    """
    client = get_client()
    try:
        dataset = client.get_dataset(dataset_id)
        resources = dataset.get('resources', [])

        schemas = {}
        for res in resources:
            schema = client.get_datastore_schema(res['id'])
            if schema:
                schemas[res['id']] = {
                    'name': res.get('name', _('No name')),
                    'format': res.get('format', 'N/A'),
                    'fields': schema
                }

        return json.dumps(schemas, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.resource("ckan://info")
def resource_info() -> str:
    """Return general CKAN portal information.

    Returns:
        JSON string containing portal version, title, and capabilities
    """
    client = get_client()
    try:
        info = client.get_site_info()
        capabilities = client.check_capabilities()

        result = {
            "url": client.url,
            "ckan_version": info.get('ckan_version', _('Unknown')),
            "site_title": info.get('site_title', 'N/A'),
            "capabilities": capabilities,
            "extensions": info.get('extensions', [])
        }

        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    mcp.run()