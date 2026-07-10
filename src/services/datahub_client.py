"""
DataHub API client for fetching metadata about your data stack.
"""

import httpx
from typing import List, Dict, Any
import logging
from src.core.config import get_settings
from src.core.exceptions import raise_datahub_error

logger = logging.getLogger(__name__)
settings = get_settings()

class DataHubClient:
    """Client for interacting with DataHub's REST API"""
    
    def __init__(self):
        self.endpoint = settings.DATAHUB_ENDPOINT.rstrip("/")
        self.token = settings.DATAHUB_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        logger.info(f"✅ DataHub client initialized for {self.endpoint}")
    
    async def get_schemas(self) -> List[Dict[str, Any]]:
        """Fetch all schemas from DataHub."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/api/v2/schemas",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                schemas = data.get("schemas", [])
                logger.info(f"✅ Fetched {len(schemas)} schemas")
                return schemas
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ DataHub HTTP error: {e}")
            raise_datahub_error(str(e))
        except Exception as e:
            logger.error(f"❌ DataHub connection error: {e}")
            raise_datahub_error(str(e))
    
    async def get_table_names(self) -> List[str]:
        """Get list of all table names from DataHub."""
        schemas = await self.get_schemas()
        tables = []
        for schema in schemas:
            for table in schema.get("tables", []):
                name = table.get("name")
                if name:
                    tables.append(name)
        logger.info(f"📊 Found {len(tables)} tables in DataHub")
        return tables
    
    async def get_column_names(self, table_name: str) -> List[str]:
        """Get column names for a specific table."""
        schemas = await self.get_schemas()
        for schema in schemas:
            for table in schema.get("tables", []):
                if table.get("name") == table_name:
                    columns = [col.get("name", "") for col in table.get("columns", [])]
                    logger.info(f"📊 Found {len(columns)} columns for table {table_name}")
                    return columns
        logger.warning(f"⚠️ Table '{table_name}' not found in DataHub")
        return []
    
    async def get_deprecated_functions(self) -> List[str]:
        """Fetch deprecated functions from DataHub."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.endpoint}/api/v2/entities?type=function&deprecated=true",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                functions = [item.get("name", "") for item in data.get("entities", [])]
                logger.info(f"🗑️ Found {len(functions)} deprecated functions")
                return functions
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch deprecated functions: {e}")
            return []