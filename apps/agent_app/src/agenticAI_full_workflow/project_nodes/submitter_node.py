# apps/agent_app/src/agenticAI_full_workflow/project_nodes/submitter_node.py
import os
import yaml
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.agenticAI_full_workflow.agent_state.state import AgentState
from shared_core.logger.logging import log

# Load Config
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
CONFIG_PATH = BASE_DIR / "apps" / "agent_app" / "config" / "config.yaml"

def load_mcp_config():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
    
    mcp_conf = config.get("mcp", {}).get("verification_server", {})
    script_rel = mcp_conf.get("script_path")
    python_rel = mcp_conf.get("python_path")
    
    if not script_rel or not python_rel:
        raise ValueError("MCP Configuration missing in config.yaml")
        
    return {
        "script": BASE_DIR / script_rel,
        "python": BASE_DIR / python_rel
    }

async def submitter_node(state: AgentState):
    log.info("--- [NODE]: SUBMITTER (Executing MCP Tool) ---")
    
    try:
        paths = load_mcp_config()
        
        server_config = {
            "verification_server": {
                "command": str(paths["python"]),
                "args": [str(paths["script"])],
                "transport": "stdio",
                "env": dict(os.environ), # Pass environment variables
            }
        }
        
        log.debug(f"MCP Server Config: {server_config}")

        # CRITICAL: Use 'async with' and 'session' to ensure the MCP server starts correctly and resources are cleaned up.
        # This invokes the "industry standard" pattern for robust resource management.
        client = MultiServerMCPClient(server_config)
        
        async with client.session("verification_server") as session:
            form_payload = state.get("extracted_data", {})
            
            # Call the specific tool defined in our MCP Server
            # The tool name matches @mcp.tool() in server.py
            log.info(f"Calling MCP Tool 'submit_verified_form' with payload: {form_payload}")
            
            result = await session.call_tool(
                "submit_verified_form", 
                arguments={"form_data": form_payload}
            )
            
            # MCP returns a CallToolResult object which has a 'content' attribute (list)
            result_text = "No response content"
            if result.content and hasattr(result.content[0], 'text'):
                 result_text = result.content[0].text
            elif result.content:
                 result_text = str(result.content)

            log.info(f"MCP Result: {result_text}")

            return {
                "messages": [("assistant", f"📢 {result_text}")]
            }
            
    except Exception as e:
        error_msg = f"❌ MCP Execution Error: {str(e)}"
        if hasattr(e, 'exceptions'):
            error_msg += f"\nInner Exceptions: {e.exceptions}"
        
        log.error(error_msg, exc_info=True)
        
        return {
            "messages": [("assistant", error_msg)]
        }