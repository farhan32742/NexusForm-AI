import re
from src.agenticAI_full_workflow.agent_state.state import AgentState
from shared_core.logger.logging import log

def validate_field(value, field_rule):
    f_type = field_rule.get("type", "string")
    
    # 1. Type Check
    if f_type in ["int", "integer"]:
        try:
            int(value)
        except: return False
            
    # 2. Regex Check (The '12345' vs 'XXXXX-XXXXXXX-X' check)
    pattern = field_rule.get("regex")
    if pattern:
        if not re.match(pattern, str(value)):
            return False
    return True

async def inspector_node(state: AgentState):
    log.info("--- [NODE]: INSPECTOR (Validating Data) ---")
    
    schema = state.get("form_schema", {})
    extracted_data = state.get("extracted_data", {})
    fields_to_check = schema.get("fields", [])
    
    missing_or_invalid = []

    for field in fields_to_check:
        f_name = field["name"]
        is_req = field.get("required", False)
        val = extracted_data.get(f_name)

        log.debug(f"CHECKING: {f_name} | Value: {val} | Required: {is_req}")

        # Logic for Missing
        if val is None or str(val).strip() == "":
            if is_req:
                log.info(f"  >> REJECTED: {f_name} is missing")
                missing_or_invalid.append(f"{f_name} (Missing)")
            continue
            
        # Logic for Invalid
        if not validate_field(val, field):
            log.info(f"  >> REJECTED: {f_name} has invalid format")
            missing_or_invalid.append(f"{f_name} (Invalid Format)")

    log.info(f"RESULT: Found {len(missing_or_invalid)} issues.")
    return {"missing_fields": missing_or_invalid}