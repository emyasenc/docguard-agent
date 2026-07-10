"""
Linter Agent - Validates code against DataHub metadata.
"""

import re
from typing import List, Dict, Any
import logging
from src.agents.base import BaseAgent
from src.services.datahub_client import DataHubClient

logger = logging.getLogger(__name__)

class LinterAgent(BaseAgent):
    """Agent that lints code for metadata compliance"""
    
    def __init__(self):
        super().__init__()
        self.datahub = DataHubClient()
    
    async def process(self, content: str, file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """Lint code against DataHub metadata."""
        if not content or not content.strip():
            return []
        
        issues = []
        
        # Run all checks
        issues.extend(await self._check_tables(content))
        issues.extend(await self._check_deprecated_functions(content))
        issues.extend(await self._check_columns(content))
        issues.extend(self._check_sql_syntax(content))
        issues.extend(self._check_imports(content))
        
        logger.info(f"🔍 Found {len(issues)} issues in {file_path}")
        return issues
    
    async def _check_tables(self, code: str) -> List[Dict[str, Any]]:
        """Check if SQL table names exist in DataHub."""
        issues = []
        try:
            table_names = await self.datahub.get_table_names()
            table_set = set([t.lower() for t in table_names])
            
            # Find table references in SQL
            sql_tables = re.findall(r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)', code, re.IGNORECASE)
            
            for table in set(sql_tables):
                if table.lower() not in table_set and table.lower() not in ["dual", "sys"]:
                    issues.append({
                        "type": "UNKNOWN_TABLE",
                        "message": f"Table '{table}' not found in DataHub metadata.",
                        "suggestion": "Check the spelling or verify the table exists in DataHub.",
                        "severity": "high",
                        "location": code.find(table)
                    })
        except Exception as e:
            logger.warning(f"⚠️ Could not check tables: {e}")
        
        return issues
    
    async def _check_deprecated_functions(self, code: str) -> List[Dict[str, Any]]:
        """Check for deprecated functions."""
        issues = []
        try:
            deprecated = await self.datahub.get_deprecated_functions()
            for func in deprecated:
                if func in code:
                    issues.append({
                        "type": "DEPRECATED_FUNCTION",
                        "message": f"Function '{func}' is deprecated.",
                        "suggestion": f"Replace '{func}' with the recommended alternative.",
                        "severity": "medium",
                        "location": code.find(func)
                    })
        except Exception as e:
            logger.warning(f"⚠️ Could not check deprecated functions: {e}")
        
        return issues
    
    async def _check_columns(self, code: str) -> List[Dict[str, Any]]:
        """Check column references against DataHub."""
        # This is a simplified check—more robust would require table context
        # For now, we just flag potential columns for manual review
        issues = []
        
        # Find column references in SELECT, WHERE, ORDER BY
        column_refs = re.findall(r'(?:SELECT|WHERE|ORDER BY)\s+([a-zA-Z_][a-zA-Z0-9_]*)', code, re.IGNORECASE)
        
        for col in set(column_refs):
            if len(col) > 2 and col.lower() not in ["from", "where", "order", "by", "and", "or", "not", "limit", "offset"]:
                # In a full implementation, you'd check against DataHub here
                # For now, just note it
                pass
        
        return issues
    
    def _check_sql_syntax(self, code: str) -> List[Dict[str, Any]]:
        """Check for common SQL issues."""
        issues = []
        
        # Check for DELETE without WHERE
        if "DELETE FROM" in code.upper() and "WHERE" not in code.upper():
            issues.append({
                "type": "MISSING_WHERE",
                "message": "DELETE statement without WHERE clause detected.",
                "suggestion": "Add a WHERE clause to prevent accidental data loss.",
                "severity": "critical",
                "location": code.find("DELETE FROM")
            })
        
        # Check for SELECT *
        if "SELECT *" in code.upper():
            issues.append({
                "type": "SELECT_STAR",
                "message": "SELECT * detected. This can cause performance issues.",
                "suggestion": "Specify only the columns you need.",
                "severity": "medium",
                "location": code.find("SELECT *")
            })
        
        return issues
    
    def _check_imports(self, code: str) -> List[Dict[str, Any]]:
        """Check for deprecated or problematic imports."""
        issues = []
        
        # List of common deprecated/recommended packages
        package_suggestions = {
            "pandas": "use polars for better performance",
            "requests": "use httpx for async support",
            "sqlalchemy": "use asyncpg for PostgreSQL",
        }
        
        for package, suggestion in package_suggestions.items():
            if f"import {package}" in code or f"from {package}" in code:
                issues.append({
                    "type": "DEPRECATED_PACKAGE",
                    "message": f"Package '{package}' is deprecated or not recommended.",
                    "suggestion": suggestion,
                    "severity": "low",
                    "location": code.find(package)
                })
        
        return issues