from src.agenticAI_full_workflow.agent_state.state import AgentState
from src.agenticAI_full_workflow.utils.form_loader import fetch_form_metadata
from shared_core.logger.logging import log

async def scout_node(state: AgentState):
    """
    Node to fetch form requirements from the external API.
    """
    log.info("--- SCOUTING FORM METADATA ---")
    
    # Check if we already have the schema in state to avoid redundant API calls
    if state.get("form_schema"):
        return state

    schema = await fetch_form_metadata()
    
    if not schema:
        # Fallback logic or error handling
        raise ValueError("Could not fetch form schema from API.")

    return {"form_schema": schema}