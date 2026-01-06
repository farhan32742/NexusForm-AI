import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Importing your refined workflow builder
from src.agenticAI_full_workflow.agent.agent_workflow import AgentWorkflowBuilder

# Load environment variables
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class QueryRequest(BaseModel):
    question: str

@app.get("/form-schema")
async def get_form_schema():
    return {
        "fields": [
            {"name": "full_name", "type": "string", "required": True, "description": "Full legal name"},
            {"name": "age", "type": "integer", "required": True, "description": "Age in years"},
            {"name": "email", "type": "string", "required": True, "description": "Email address"},
            {"name": "destination", "type": "string", "required": True, "description": "Travel destination"},
        ]
    }

@app.post("/query")
async def query_travel_agent(query:QueryRequest):
    try:
        print(query)
        graph = AgentWorkflowBuilder()
        react_app=graph()
        #react_app = graph.build_graph()

        png_graph = react_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)

        print(f"Graph saved as 'my_graph.png' in {os.getcwd()}")
        # Assuming request is a pydantic object like: {"question": "your text"}
        messages={"messages": [query.question]}
        output = react_app.invoke(messages)

        # If result is dict with messages:
        if isinstance(output, dict) and "messages" in output:
            final_output = output["messages"][-1].content  # Last AI response
        else:
            final_output = str(output)
        
        return {"answer": final_output}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})