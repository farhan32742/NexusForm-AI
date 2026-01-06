# mcp_servers/verification_mcp/src/tools/db_handler.py
import httpx
import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def post_to_mysql_api(data: Dict[str, Any]) -> str:
    url = os.getenv("FORM_SUBMIT_URL")
    
    async with httpx.AsyncClient() as client:
        try:
            # INDUSTRY TIP: Some backends say they want Form but actually need JSON 
            # or vice versa. We will force headers to be safe.
            print(f"[MCP DEBUG]: Posting data to {url}: {data}")
            
            # Try sending as Form Data first (matches your Swagger screenshot)
            response = await client.post(
                url, 
                data=data, 
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15.0
            )
            
            # If the backend actually wanted JSON, a 422 might happen. 
            # Let's handle that or just raise for status.
            response.raise_for_status()
            
            return f"✅ Success: Data for {data.get('full_name')} saved."

        except httpx.HTTPStatusError as e:
            # Catch the 422 and explain it
            error_detail = e.response.text
            return f"❌ Backend Error ({e.response.status_code}): {error_detail}"
        except Exception as e:
            return f"❌ Connection Error: {str(e)}"