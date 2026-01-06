from pydantic import BaseModel, Field, create_model, ConfigDict
from typing import Optional, Type

def create_dynamic_model(schema_from_api: dict) -> Type[BaseModel]:
    fields = {}
    api_fields = schema_from_api.get("fields", [])
    
    for field in api_fields:
        name = field["name"]
        f_type = str(field.get("type", "string")).lower()
        
        # Handle OpenAPI "integer" vs Python "int"
        if f_type in ["int", "integer"]:
            python_type = Optional[int]
        elif f_type in ["number", "float"]:
            python_type = Optional[float]
        else:
            python_type = Optional[str]
            
        fields[name] = (python_type, Field(default=None))

    return create_model(
        "UserFormData", 
        __config__=ConfigDict(extra="forbid"), 
        **fields
    )