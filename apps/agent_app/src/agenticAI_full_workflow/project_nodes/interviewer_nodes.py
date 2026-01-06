from src.agenticAI_full_workflow.agent_state.state import AgentState
from src.agenticAI_full_workflow.utils.model_loader import ModelLoader

model_loader = ModelLoader()
llm = model_loader.load_llm()

async def interviewer_node(state: AgentState):
    """
    The Voice: Takes the list of missing/invalid fields and asks the user.
    """
    print("--- [NODE]: INTERVIEWER (Requesting Clarification) ---")
    
    missing_info = state.get("missing_fields", [])
    
    # 1. Create a prompt for the LLM to ask naturally
    system_prompt = (
        "You are a professional form-filling assistant. The following fields are either missing "
        "or have invalid formats. Please ask the user to provide or correct them in a friendly, "
        "concise way.\n\n"
        f"Issues found: {', '.join(missing_info)}"
    )
    
    messages = [("system", system_prompt)] + state["messages"]
    response = await llm.ainvoke(messages)
    
    return {
        "messages": [response]
    }