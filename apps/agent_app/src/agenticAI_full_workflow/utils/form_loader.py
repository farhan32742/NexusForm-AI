import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

def parse_openapi_to_fields(openapi_json: dict):
    try:
        # Navigate to the specific schema
        schema_path = openapi_json['components']['schemas']['Body_handle_form_submit_post']
        properties = schema_path.get('properties', {})
        required_list = schema_path.get('required', [])

        fields = []
        for name, info in properties.items():
            # Get the pattern (regex) if it exists in the Swagger
            pattern = info.get("pattern") or info.get("format")
            
            fields.append({
                "name": name,
                "type": info.get("type", "string"),
                "required": name in required_list,
                "label": info.get("title", name),
                "regex": pattern  # Now capturing regex from API
            })
        return {"fields": fields}
    except Exception as e:
        print(f"[ERROR]: Parser failed: {e}")
        return {"fields": []}

async def fetch_form_metadata():
    url = os.getenv("FORM_GET_SCHEMA_URL")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            return parse_openapi_to_fields(response.json())
        except Exception as e:
            print(f"Error fetching schema: {e}")
            return None