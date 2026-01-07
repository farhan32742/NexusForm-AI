import json
from src.agenticAI_full_workflow.agent_state.state import AgentState
from src.agenticAI_full_workflow.utils.model_loader import ModelLoader
from src.agenticAI_full_workflow.prompt_library.prompts import FORM_FILLER_SYSTEM_PROMPT
from src.agenticAI_full_workflow.schemas.form_schema import create_dynamic_model
from shared_core.logger.logging import log
from langchain_core.messages import trim_messages

# Load the model once
model_loader = ModelLoader()
llm = model_loader.load_llm()

async def agent_node(state: AgentState):
    log.info("--- [NODE]: AGENT (Extracting Data) ---")
    
    api_schema = state.get("form_schema", {})
    trimmed_messages = state["messages"][-6:] 
    
    # DEBUG: See what the Scout actually brought back
    log.debug(f"Schema found in Agent Node: {api_schema}")

    if not api_schema or "fields" not in api_schema:
        log.error("No fields found in schema! Agent cannot extract data.")
        return state

    DynamicModel = create_dynamic_model(api_schema)
    
    # Help the LLM by listing the exact keys it needs to find
    field_names = [f['name'] for f in api_schema['fields']]
    
    # Inside agent_node.py
    system_message = (
        f"{FORM_FILLER_SYSTEM_PROMPT}\n\n"
        f"TARGET FIELDS: {', '.join(field_names)}\n"
        "NOTE: User might say 'CNIC' for 'id_card'. Map it correctly.\n"
        "Return ONLY JSON."
    )

    messages = [("system", system_message)] + trimmed_messages
    structured_llm = llm.with_structured_output(DynamicModel) 
    
    try:
        response_model = await structured_llm.ainvoke(messages)
        new_data_chunk = response_model.model_dump(exclude_none=True)
        
        updated_data = state.get("extracted_data", {}).copy()
        updated_data.update(new_data_chunk)

        # We return the trimmed messages so the state doesn't grow forever
        return {
            "extracted_data": updated_data,
            "messages": trimmed_messages + [("assistant", f"Updated: {new_data_chunk}")]
        }
    except Exception as e:
        log.error(f"AGENT ERROR: {e}")
        return state