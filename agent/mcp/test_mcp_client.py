"""
Test script to verify FastMCP Server functionality for BigQuery tables and graph queries.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agent.mcp.server import (
    mcp,
    mcp_inspect_dataset_schema,
    mcp_trace_referral_bounce_loop,
    mcp_find_compliant_45day_pathway,
    mcp_run_equity_audit
)

def test_mcp_tools():
    print("="*75)
    print("  TESTING BIGQUERY MCP SERVER: qwiklabs-gcp-04-5956a6cfcbdf.a4i_early_intervention")
    print("="*75)
    
    # 1. Test Schema Inspection
    schema = mcp_inspect_dataset_schema()
    print("\n[MCP Tool 1: bigquery_inspect_dataset_schema]")
    print(f"Dataset: {schema['project_id']}.{schema['dataset_id']}")
    print(f"Discovered Tables: {list(schema['tables'].keys())}")
    
    # 2. Test Trace Referral Loop
    trace = mcp_trace_referral_bounce_loop(state_code="MS", case_chain_id="CHAIN-MS-009")
    print("\n[MCP Tool 2: trace_referral_bounce_loop]")
    print(f"Status: Success | Chain: {trace['chains'][0]['case_chain_id']} | Wait Days: {trace['chains'][0]['cumulative_wait_days']} (Breached: {trace['chains'][0]['is_breached']})")
    
    # 3. Test Compliant Pathway Finder
    pathway = mcp_find_compliant_45day_pathway(
        child_age_months=20,
        home_tract_geoid="28011950701",
        requires_medicaid=True,
        requires_bilingual=True,
        state_code="MS"
    )
    print("\n[MCP Tool 3: find_compliant_45day_pathway]")
    print(f"Status: Success | Cumulative Days: {pathway['cumulative_wait_days']} | Compliant: {pathway['is_compliant']}")
    print(f"Sequence: {' -> '.join([s['name'].split()[0] for s in pathway['recommended_pathway']])}")
    
    # 4. Test Equity Audit
    equity = mcp_run_equity_audit(home_tract_geoid="28011950701", state_code="MS")
    print("\n[MCP Tool 4: run_equity_audit]")
    print(f"Status: Success | County: {equity['county_name']} | Poverty Rate: {equity['neighborhood_poverty_rate_pct']}%")
    
    print("\n" + "="*75)
    print("✓ BigQuery MCP tools verified successfully!")
    print("="*75)

if __name__ == "__main__":
    test_mcp_tools()
