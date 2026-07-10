"""
Tests for the LinterAgent.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.linter import LinterAgent

@pytest.mark.asyncio
async def test_linter_unknown_table():
    """Test that unknown tables are flagged."""
    agent = LinterAgent()
    
    # Mock the DataHub client to return a known table list
    with patch.object(agent.datahub, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
        mock_get_tables.return_value = ["users", "orders", "products"]
        
        code = "SELECT * FROM fake_table WHERE id = 1"
        issues = await agent.process(code, "test.py")
        
        # Should flag unknown table
        unknown_table_issues = [i for i in issues if i.get("type") == "UNKNOWN_TABLE"]
        assert len(unknown_table_issues) >= 1
        assert "fake_table" in unknown_table_issues[0]["message"]

@pytest.mark.asyncio
async def test_linter_select_star():
    """Test that SELECT * is flagged."""
    agent = LinterAgent()
    
    # Mock DataHub to return a known table list
    with patch.object(agent.datahub, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
        mock_get_tables.return_value = ["users", "orders", "products"]
        
        code = "SELECT * FROM users"
        issues = await agent.process(code, "test.py")
        
        select_star_issues = [i for i in issues if i.get("type") == "SELECT_STAR"]
        assert len(select_star_issues) >= 1

@pytest.mark.asyncio
async def test_linter_missing_where():
    """Test that DELETE without WHERE is flagged."""
    agent = LinterAgent()
    
    # Mock DataHub to return a known table list
    with patch.object(agent.datahub, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
        mock_get_tables.return_value = ["users", "orders", "products"]
        
        code = "DELETE FROM users"
        issues = await agent.process(code, "test.py")
        
        missing_where_issues = [i for i in issues if i.get("type") == "MISSING_WHERE"]
        assert len(missing_where_issues) >= 1

@pytest.mark.asyncio
async def test_linter_empty_content():
    """Test that empty content returns no issues."""
    agent = LinterAgent()
    issues = await agent.process("", "empty.py")
    assert len(issues) == 0

@pytest.mark.asyncio
async def test_linter_known_table_no_issue():
    """Test that known tables don't raise issues."""
    agent = LinterAgent()
    
    # Mock DataHub to return a known table list
    with patch.object(agent.datahub, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
        mock_get_tables.return_value = ["users", "orders", "products"]
        
        code = "SELECT * FROM users WHERE id = 1"
        issues = await agent.process(code, "test.py")
        
        unknown_table_issues = [i for i in issues if i.get("type") == "UNKNOWN_TABLE"]
        assert len(unknown_table_issues) == 0