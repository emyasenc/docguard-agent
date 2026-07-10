"""
Doc Validator Agent - Validates documentation against DataHub metadata.
"""

import re
from typing import List, Dict, Any
import logging
from src.agents.base import BaseAgent
from src.services.datahub_client import DataHubClient

logger = logging.getLogger(__name__)

class DocValidatorAgent(BaseAgent):
    """Agent that validates documentation for metadata compliance"""
    
    def __init__(self):
        super().__init__()
        self.datahub = DataHubClient()
    
    async def process(self, content: str, file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """Validate documentation against DataHub metadata."""
        if not content or not content.strip():
            return []
        
        issues = []
        
        # Run all checks
        issues.extend(await self._check_table_references(content))
        issues.extend(await self._check_column_references(content))
        issues.extend(self._check_deprecated_terms(content))
        issues.extend(self._check_missing_sections(content))
        
        logger.info(f"📝 Found {len(issues)} documentation issues in {file_path}")
        return issues
    
    async def _check_table_references(self, content: str) -> List[Dict[str, Any]]:
        """Check if table names mentioned in docs exist in DataHub."""
        issues = []
        try:
            table_names = await self.datahub.get_table_names()
            table_set = set([t.lower() for t in table_names])
            
            # Find table mentions
            table_mentions = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:table|schema|dataset)\b', content, re.IGNORECASE)
            
            for mention in table_mentions:
                if mention.lower() not in table_set:
                    issues.append({
                        "type": "MISSING_TABLE",
                        "message": f"Table '{mention}' mentioned in docs but not found in DataHub.",
                        "suggestion": "Verify the table name or add it to DataHub.",
                        "severity": "medium",
                        "location": content.find(mention)
                    })
        except Exception as e:
            logger.warning(f"⚠️ Could not check table references: {e}")
        
        return issues
    
    async def _check_column_references(self, content: str) -> List[Dict[str, Any]]:
        """Check if column names mentioned in docs exist."""
        issues = []
        
        # Find column mentions
        column_mentions = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s+(?:column|field|attribute)\b', content, re.IGNORECASE)
        
        # Simplified check—would be more thorough with specific tables
        common_columns = {"id", "name", "date", "time", "created_at", "updated_at"}
        for mention in set(column_mentions):
            if mention.lower() not in common_columns and len(mention) > 2:
                issues.append({
                    "type": "UNKNOWN_COLUMN",
                    "message": f"Column '{mention}' referenced in docs. Verify it exists in the schema.",
                    "suggestion": "Check the column name against the actual schema.",
                    "severity": "low",
                    "location": content.find(mention)
                })
        
        return issues
    
    def _check_deprecated_terms(self, content: str) -> List[Dict[str, Any]]:
        """Check for deprecated terms in documentation."""
        deprecated_terms = [
            "old_api", "legacy", "deprecated_function", "v1_endpoint",
            "obsolete", "outdated", "old_schema"
        ]
        
        issues = []
        for term in deprecated_terms:
            if term.lower() in content.lower():
                issues.append({
                    "type": "DEPRECATED_TERM",
                    "message": f"Term '{term}' is deprecated or outdated.",
                    "suggestion": f"Replace '{term}' with the recommended alternative.",
                    "severity": "medium",
                    "location": content.lower().find(term.lower())
                })
        
        return issues
    
    def _check_missing_sections(self, content: str) -> List[Dict[str, Any]]:
        """Check for missing required documentation sections."""
        required_sections = [
            "Description",
            "Usage",
            "Parameters",
            "Response",
            "Example"
        ]
        
        issues = []
        content_lower = content.lower()
        
        for section in required_sections:
            if section.lower() not in content_lower:
                issues.append({
                    "type": "MISSING_SECTION",
                    "message": f"Missing required section: '{section}'",
                    "suggestion": f"Add '{section}' section to the documentation.",
                    "severity": "high",
                    "location": 0
                })
        
        return issues