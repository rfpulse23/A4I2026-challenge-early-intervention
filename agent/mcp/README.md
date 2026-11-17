# First Milestones Referral Graph MCP Server

Model Context Protocol (MCP) Server exposing Early Intervention referral network graph queries, bottleneck detection, and equity auditing tools over standard MCP protocol (stdio/SSE).

## Tools Exposed

1. **`trace_referral_bounce_loop`**:
   - Traverses multi-hop referral chains (`2..4` hops) to diagnose paper-fax bottlenecks and multi-hop bounce loops exceeding the 45-day federal IDEA Part C clock.
2. **`find_compliant_45day_pathway`**:
   - Discovers an optimal `<=45-day` compliant referral pathway for an incoming toddler matching age, Medicaid, and Spanish bilingual requirements.
3. **`run_equity_audit`**:
   - Audits the child's home neighborhood demographics (poverty rate, zero-vehicle rate, racial/ethnic shares) against state averages to detect transport and systemic access barriers.

## Resources Exposed

- `referral://standards/idea-part-c`: Statutory IDEA Part C 45-day timeline and equity compliance rules (`34 CFR § 303.310`).

## Running & Testing

```bash
# Run server standalone over stdio
python repo_template/mcp_server/server.py

# Test server tools
python repo_template/mcp_server/test_mcp_client.py

# Test ADK McpToolset integration
python repo_template/agent/mcp_adk_connector.py
```
