from typing import Dict, Any
from mcp_servers.verification_mcp.src.tools.db_handler import DatabaseHandler

db = DatabaseHandler()

async def process_submission(form_data: Dict[str, Any]) -> str:
    """
    Business logic for final verification before DB insertion.
    """
    if not form_data:
        return "Error: Received empty data."

    # Final DB call
    success = await db.save_form_data(table_name="user_submissions", data=form_data)
    
    if success:
        # Create a detailed confirmation message
        summary = ", ".join([f"{k}: {v}" for k, v in form_data.items()])
        return f"Successfully recorded {len(form_data)} fields: [{summary}]"
    
    return "Error: Database insertion failed."