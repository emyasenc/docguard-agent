"""
Tests for the DocValidatorAgent.
"""

import pytest
from src.agents.doc_validator import DocValidatorAgent

@pytest.mark.asyncio
async def test_doc_missing_sections():
    """Test that missing sections are flagged."""
    agent = DocValidatorAgent()
    doc = "# Test Doc\n\nThis is a test."
    issues = await agent.process(doc, "test.md")
    
    missing_section_issues = [i for i in issues if i.get("type") == "MISSING_SECTION"]
    assert len(missing_section_issues) >= 1

@pytest.mark.asyncio
async def test_doc_deprecated_term():
    """Test that deprecated terms are flagged."""
    agent = DocValidatorAgent()
    doc = "Use the old_api for legacy endpoints."
    issues = await agent.process(doc, "test.md")
    
    deprecated_issues = [i for i in issues if i.get("type") == "DEPRECATED_TERM"]
    assert len(deprecated_issues) >= 1

@pytest.mark.asyncio
async def test_doc_empty_content():
    """Test that empty content returns no issues."""
    agent = DocValidatorAgent()
    issues = await agent.process("", "empty.md")
    assert len(issues) == 0