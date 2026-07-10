"""
GitHub webhook receiver for DocGuard.
"""

import hmac
import hashlib
import httpx
from fastapi import APIRouter, Request, HTTPException, Header
from src.agents.linter import LinterAgent
from src.agents.doc_validator import DocValidatorAgent
from src.services.github_client import GitHubClient
from src.core.config import get_settings
from src.core.logging import setup_logging
import logging
import os

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
settings = get_settings()

@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(...),
    x_hub_signature_256: str = Header(None)
):
    """Receive GitHub webhook events."""
    
    # ============================================
    # SIGNATURE VERIFICATION (with test mode)
    # ============================================
    # Skip verification in test mode or if secret is not set
    is_test_mode = os.getenv("ENVIRONMENT") == "test" or os.getenv("TESTING") == "true"
    
    if settings.GITHUB_WEBHOOK_SECRET and not is_test_mode:
        body = await request.body()
        expected = hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not x_hub_signature_256:
            logger.warning("❌ Missing signature header")
            raise HTTPException(401, "Missing webhook signature")
        
        if not hmac.compare_digest(x_hub_signature_256, f"sha256={expected}"):
            logger.warning("❌ Invalid webhook signature")
            raise HTTPException(401, "Invalid webhook signature")
    else:
        logger.info("🔓 Webhook signature verification disabled (test mode)")
    
    # Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"❌ Invalid JSON payload: {e}")
        raise HTTPException(400, "Invalid JSON payload")
    
    logger.info(f"📨 Received webhook: {x_github_event}")
    
    # Only process pull_request events
    if x_github_event == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            await process_pull_request(payload)
            return {"status": "processing", "event": "pull_request", "action": action}
    
    return {"status": "ignored", "event": x_github_event}

async def process_pull_request(payload: dict):
    """Process a pull request event."""
    repo_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    
    # Initialize agents and clients
    linter = LinterAgent()
    doc_validator = DocValidatorAgent()
    github = GitHubClient()
    
    # Get PR files
    files = await github.get_pr_files(repo_name, pr_number)
    
    all_issues = []
    lint_count = 0
    doc_count = 0
    
    for file_info in files:
        filename = file_info.get("filename", "")
        raw_url = file_info.get("raw_url")
        status = file_info.get("status", "")
        
        if status == "removed":
            continue
        
        if not raw_url:
            continue
        
        # Fetch file content
        async with httpx.AsyncClient() as client:
            response = await client.get(raw_url)
            if response.status_code != 200:
                continue
            
            content = response.text
            
            # Determine file type and run appropriate agent
            if filename.endswith((".py", ".js", ".ts", ".go", ".rs", ".java", ".sql")):
                issues = await linter.process(content, filename)
                all_issues.extend(issues)
                lint_count += len(issues)
            elif filename.endswith((".md", ".rst", ".txt")):
                issues = await doc_validator.process(content, filename)
                all_issues.extend(issues)
                doc_count += len(issues)
    
    # Generate report and post comment
    report = generate_report(all_issues, lint_count, doc_count)
    await github.post_comment(repo_name, pr_number, report)
    logger.info(f"✅ Processed PR #{pr_number} with {len(all_issues)} issues")

def generate_report(issues: list, lint_count: int, doc_count: int) -> str:
    """Generate a comprehensive report for the PR."""
    
    lines = [
        "## 🛡️ DocGuard Report\n",
        f"**Code Issues:** {lint_count}",
        f"**Documentation Issues:** {doc_count}",
        f"**Total Issues:** {len(issues)}\n",
        "---\n"
    ]
    
    if not issues:
        lines.append("✅ **DocGuard** found no issues in this PR. Great work!")
        return "\n".join(lines)
    
    # Group by severity
    high = [i for i in issues if i.get("severity") == "critical"]
    medium = [i for i in issues if i.get("severity") in ["high", "medium"]]
    low = [i for i in issues if i.get("severity") == "low"]
    
    if high:
        lines.append("### 🔴 Critical Issues (Must Fix)\n")
        for issue in high[:5]:
            lines.append(f"- **{issue.get('message', '')}**")
            lines.append(f"  - Suggestion: {issue.get('suggestion', '')}\n")
    
    if medium:
        lines.append("### 🟡 Medium Issues (Should Fix)\n")
        for issue in medium[:5]:
            lines.append(f"- {issue.get('message', '')}")
            lines.append(f"  - Suggestion: {issue.get('suggestion', '')}\n")
    
    if low:
        lines.append("### 🟢 Low Priority Issues\n")
        for issue in low[:3]:
            lines.append(f"- {issue.get('message', '')}\n")
    
    if len(issues) > 10:
        lines.append(f"\n*... and {len(issues) - 10} more issues.*")
    
    lines.append("\n---\n*Report generated by DocGuard.*")
    return "\n".join(lines)