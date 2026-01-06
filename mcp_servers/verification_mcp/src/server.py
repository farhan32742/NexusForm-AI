# mcp_servers/verification_mcp/src/server.py
from fastmcp import FastMCP
try:
    from .tools.db_handler import post_to_mysql_api
except ImportError:
    from tools.db_handler import post_to_mysql_api
from typing import Dict, Any

# Initialize FastMCP Server
mcp = FastMCP("Verification_Server")

@mcp.tool()
async def submit_verified_form(form_data: Dict[str, Any]) -> str:
    """
    Production tool to submit verified form data to the MySQL backend.
    Accepts a dictionary of any size containing user details.
    """
    # This tool is only called after Human-in-the-loop approval
    result = await post_to_mysql_api(form_data)
    return result

if __name__ == "__main__":
    mcp.run()