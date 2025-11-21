"""Intelligent CKAN client with robust error handling and retry logic."""
import logging
import os
import time
from functools import wraps
from typing import Any, Dict, List, Optional

from ckanapi import CKANAPIError, NotAuthorized, NotFound, RemoteCKAN, ValidationError

try:
    from .i18n import _
except ImportError:
    from i18n import _

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = "ckan-mcp-server/1.0 (+https://github.com/mjanez/ckan-mcp-server)"
MAX_RETRIES = 3
RETRY_DELAY = 1.0

GEO_FORMATS = {'shp', 'kml', 'geojson', 'wms', 'wfs', 'wcs', 'gpkg', 'gml', 'kmz'}


class CKANClientError(Exception):
    """Base exception for CKAN client errors."""
    pass


def retry_on_error(max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY):
    """Decorator to retry failed operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds

    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning("Attempt %d/%d failed: %s. Retrying in %ss...", attempt + 1, max_retries, e, wait_time)
                        time.sleep(wait_time)
                    else:
                        logger.error("All attempts failed for %s", func.__name__)
                except (NotFound, NotAuthorized, ValidationError):
                    raise
            raise CKANClientError(_("Operation failed after {} attempts").format(max_retries)) from last_exception
        return wrapper
    return decorator


class CKANClient:
    """Intelligent wrapper over ckanapi with advanced features.

    Features:
    - Automatic retry logic
    - Portal capability detection
    - Helpers for common operations
    - Metadata caching
    """

    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Initialize CKAN client.

        Args:
            url: CKAN portal URL (defaults to CKAN_URL env var)
            api_key: CKAN API key for authentication (defaults to CKAN_API_KEY env var)
            user_agent: Custom user agent string
        """
        self.url = url or os.getenv("CKAN_URL", "https://demo.ckan.org")
        self.api_key = api_key or os.getenv("CKAN_API_KEY")
        self.user_agent = user_agent or DEFAULT_USER_AGENT

        self._client = RemoteCKAN(
            self.url,
            apikey=self.api_key,
            user_agent=self.user_agent
        )

        self._capabilities: Optional[Dict[str, bool]] = None

        logger.info("CKAN client initialized for: %s", self.url)

    @property
    def action(self):
        """Direct access to the actions API."""
        return self._client.action

    @retry_on_error()
    def get_site_info(self) -> Dict[str, Any]:
        """Get CKAN site information."""
        try:
            return self.action.status_show()
        except Exception as e:
            logger.warning("Could not get status_show: %s", e)
            return {}

    @retry_on_error()
    def search_datasets(
        self,
        query: str = "*:*",
        filters: Optional[Dict[str, Any]] = None,
        facets: Optional[Dict[str, int]] = None,
        rows: int = 10,
        start: int = 0,
        sort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Advanced dataset search with filter and facet support.

        Args:
            query: SOLR query (default: all)
            filters: Filter dictionary (converted to fq)
            facets: Facets to include {field: limit}
            rows: Number of results
            start: Pagination offset
            sort: Sort field
        """
        params = {
            'q': query,
            'rows': rows,
            'start': start,
            'include_private': False
        }

        if filters:
            fq_list = []
            for key, value in filters.items():
                if isinstance(value, list):
                    values_str = " OR ".join([f'{key}:"{v}"' for v in value])
                    fq_list.append(f"({values_str})")
                else:
                    fq_list.append(f'{key}:"{value}"')
            params['fq'] = " AND ".join(fq_list)

        if facets:
            params['facet.field'] = list(facets.keys())
            for field, limit in facets.items():
                params[f'f.{field}.facet.limit'] = limit

        if sort:
            params['sort'] = sort

        return self.action.package_search(**params)

    @retry_on_error()
    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Get complete information for a dataset."""
        return self.action.package_show(id=dataset_id)

    @retry_on_error()
    def get_resource(self, resource_id: str) -> Dict[str, Any]:
        """Get resource information."""
        return self.action.resource_show(id=resource_id)

    @retry_on_error()
    def get_organization(self, org_id: str) -> Dict[str, Any]:
        """Get organization information."""
        return self.action.organization_show(id=org_id)

    @retry_on_error()
    def get_group(self, group_id: str) -> Dict[str, Any]:
        """Get group information."""
        return self.action.group_show(id=group_id)

    def has_datastore(self, resource_id: str) -> bool:
        """Check if a resource has active DataStore.

        Args:
            resource_id: Resource ID to check

        Returns:
            True if resource has DataStore enabled, False otherwise
        """
        try:
            _result = self.action.datastore_search(resource_id=resource_id, limit=0)
            return True
        except (NotFound, CKANAPIError):
            return False

    @retry_on_error()
    def datastore_search(
        self,
        resource_id: str,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Search DataStore with filters.

        Args:
            resource_id: Resource ID to search
            limit: Maximum number of records to return
            offset: Number of records to skip
            filters: Dictionary of field filters
            fields: List of fields to include in response

        Returns:
            DataStore search results
        """
        params = {
            'resource_id': resource_id,
            'limit': limit,
            'offset': offset
        }

        if filters:
            params['filters'] = filters

        if fields:
            params['fields'] = fields

        return self.action.datastore_search(**params)

    @retry_on_error()
    def datastore_search_sql(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query on DataStore.

        Note: Requires portal to have datastore_search_sql enabled.
        """
        return self.action.datastore_search_sql(sql=sql)

    def get_datastore_schema(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get schema for a DataStore resource.

        Useful for generating intelligent SQL queries.
        """
        try:
            result = self.action.datastore_search(resource_id=resource_id, limit=0)
            return result.get('fields', [])
        except (NotFound, CKANAPIError) as e:
            logger.warning("Could not get schema for %s: %s", resource_id, e)
            return None

    def is_geospatial_dataset(self, dataset: Dict[str, Any]) -> bool:
        """Detect if a dataset contains geospatial data.

        Args:
            dataset: Dataset dictionary

        Returns:
            True if dataset contains geospatial resources or metadata
        """
        for resource in dataset.get('resources', []):
            format_lower = resource.get('format', '').lower()
            if format_lower in GEO_FORMATS:
                return True

        extras = {e['key']: e['value'] for e in dataset.get('extras', [])}
        geo_indicators = ['spatial', 'bbox', 'spatial_coverage', 'geographic_coverage']

        return any(indicator in extras for indicator in geo_indicators)

    def get_geospatial_resources(self, dataset: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract only geospatial resources from a dataset.

        Args:
            dataset: Dataset dictionary

        Returns:
            List of geospatial resource dictionaries
        """
        geo_resources = []
        for resource in dataset.get('resources', []):
            format_lower = resource.get('format', '').lower()
            if format_lower in GEO_FORMATS:
                geo_resources.append(resource)
        return geo_resources

    def check_capabilities(self) -> Dict[str, bool]:
        """Detect CKAN portal capabilities.

        Useful for adapting functionality based on version.
        """
        if self._capabilities is not None:
            return self._capabilities

        capabilities = {
            'datastore': False,
            'datapusher': False,
            'spatial': False,
            'dcat': False,
            'harvest': False
        }

        try:
            self.action.datastore_search(resource_id='_table_metadata', limit=0)
            capabilities['datastore'] = True
        except Exception:
            pass

        try:
            status = self.get_site_info()
            extensions = status.get('extensions', [])

            capabilities['spatial'] = 'spatial_metadata' in extensions or 'spatial_query' in extensions
            capabilities['dcat'] = 'dcat' in extensions
            capabilities['harvest'] = 'harvest' in extensions
            capabilities['datapusher'] = 'datapusher' in extensions
        except Exception:
            pass

        self._capabilities = capabilities
        logger.info("Capabilities detected: %s", capabilities)
        return capabilities

    def format_dataset_summary(self, dataset: Dict[str, Any]) -> str:
        """Format a dataset for readable display.

        Args:
            dataset: Dataset dictionary

        Returns:
            Formatted multiline string with dataset summary
        """
        is_geo = self.is_geospatial_dataset(dataset)
        icon = "🌍" if is_geo else "📦"

        org = dataset.get('organization') or {}
        org_title = org.get('title', _('No organization'))

        resources_formats = [r['format'] for r in dataset.get('resources', [])]

        lines = [
            f"{icon} **{dataset.get('title', _('No title'))}**",
            f"- {_('ID')}: `{dataset['id']}`",
            f"- {_('Organization')}: {org_title}",
            f"- {_('Resources')}: {', '.join(resources_formats) if resources_formats else _('None')}",
            f"- {_('License')}: {dataset.get('license_title', _('Not specified'))}",
        ]

        if dataset.get('notes'):
            lines.append(f"- {_('Description')}: {dataset['notes'][:200]}...")

        return "\n".join(lines)


def get_client() -> CKANClient:
    """Factory function to get a CKAN client.

    Returns:
        Initialized CKANClient instance
    """
    return CKANClient()
