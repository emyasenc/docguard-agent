"""
GitHub API client for DocGuard.
Handles PR file fetching and commenting.
"""

import httpx
import base64
from typing import List, Dict, Any
import logging
from src.core.config import get_settings
from src.core.exceptions import raise_github_error

logger = logging.getLogger(__name__)
settings = get_settings()

class GitHubClient:
    """Client for interacting with GitHub's REST API"""
    
    def __init__(self):
        self.token = settings.GITHUB_TOKEN
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        if not self.token:
            logger.warning("⚠️ GITHUB_TOKEN not set. GitHub API calls will fail.")
        else:
            logger.info("✅ GitHub client initialized")
    
    async def get_pr_files(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get list of files changed in a PR."""
        if not self.token:
            logger.error("❌ GITHUB_TOKEN not set")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                files = response.json()
                logger.info(f"📁 Retrieved {len(files)} files from PR #{pr_number}")
                return files
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ GitHub API error: {e}")
            raise_github_error(str(e))
        except Exception as e:
            logger.error(f"❌ GitHub connection error: {e}")
            raise_github_error(str(e))
    
    async def post_comment(self, repo: str, pr_number: int, comment: str) -> Dict[str, Any]:
        """Post a comment on a PR."""
        if not self.token:
            logger.error("❌ GITHUB_TOKEN not set")
            return {"error": "GITHUB_TOKEN not set"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments",
                    headers=self.headers,
                    json={"body": comment},
                    timeout=10.0
                )
                response.raise_for_status()
                logger.info(f"✅ Posted comment on PR #{pr_number}")
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to post comment: {e}")
            raise_github_error(str(e))
        except Exception as e:
            logger.error(f"❌ Comment error: {e}")
            raise_github_error(str(e))
    
    async def get_file_content(self, repo: str, file_path: str, ref: str = "main") -> str:
        """Get content of a file from a repo."""
        if not self.token:
            return ""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/contents/{file_path}?ref={ref}",
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                content = base64.b64decode(data.get("content", "")).decode("utf-8")
                logger.info(f"📄 Retrieved content for {file_path}")
                return content
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch {file_path}: {e}")
            return ""