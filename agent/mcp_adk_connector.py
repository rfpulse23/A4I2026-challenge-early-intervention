"""
ADK Agent connected to the Referral Graph MCP Server via McpToolset.
Demonstrates standard MCP stdio protocol integration with Google ADK.
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google.adk.agents import Agent
from google.adk.tools import McpToolset
from mcp import StdioServerParameters

def get_mcp_toolset() -> McpToolset:
    """
    Spawns the local FastMCP server via stdio and returns an ADK McpToolset.
    """
    server_script = str(Path(__file__).resolve().parent / "mcp" / "server.py")
    python_bin = sys.executable

    server_params = StdioServerParameters(
        command=python_bin,
        args=[server_script],
        env=dict(os.environ)
    )
    
    return McpToolset(connection_params=server_params)

def create_mcp_powered_agent(model_name: str = "gemini-2.5-flash") -> Agent:
    """
    Creates an ADK agent equipped with the Referral Graph MCP Server tools.
    """
    toolset = get_mcp_toolset()
    
    agent = Agent(
        name="mcp_early_intervention_coordinator",
        description="ADK Agent powered by FastMCP Referral Graph Server tools.",
        model=model_name,
        instruction="You are an Early Intervention intake assistant using tools provided by the Referral Graph MCP server.",
        tools=[toolset]
    )
    return agent

if __name__ == "__main__":
    print("Testing ADK + MCP Connector setup...")
    agent = create_mcp_powered_agent()
    print(f"Agent successfully configured: {agent.name}")
    print("McpToolset registered successfully!")
