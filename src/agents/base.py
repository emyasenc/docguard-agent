"""
Base agent class for all DocGuard agents.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all DocGuard agents."""
    
    def __init__(self):
        self.name = self.__class__.__name__
        logger.info(f"🤖 {self.name} initialized")
    
    @abstractmethod
    async def process(self, content: str, file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Process content and return a list of issues.
        
        Args:
            content: The content to process (code, docs, etc.)
            file_path: The path of the file being processed
            **kwargs: Additional arguments
            
        Returns:
            List of issue dicts with keys: type, message, suggestion, severity, location
        """
        pass
    
    def _create_issue(self, issue_type: str, message: str, suggestion: str, severity: str, location: int = 0) -> Dict[str, Any]:
        """Helper to create a standardized issue dict."""
        return {
            "type": issue_type,
            "message": message,
            "suggestion": suggestion,
            "severity": severity,
            "location": location
        }