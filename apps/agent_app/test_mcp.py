import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure the app can find the 'src' folder
sys.path.append(os.path.join(os.getcwd(), "src"))

from agenticAI_full_workflow.agent.agent_workflow import AgentWorkflowBuilder

load_dotenv()

import random
import time

async def run_test():
    print("STARTING FULL END-TO-END MCP TEST")
    builder = AgentWorkflowBuilder()
    graph = builder.build()
    
    # Generate dynamic data to prevent "Duplicate Entry" errors
    # INDUSTRY STANDARD: Use unique identifiers for integration tests
    unique_id = int(time.time())
    dynamic_email = f"farhan_{unique_id}@test.com"
    dynamic_name = "Farhan Khan"
    
    # 1. Provide initial data 
    # We provide ALL data upfront now, as the user requested.
    user_input = f"My name is {dynamic_name}, my age is 34, and my email is {dynamic_email}."
    
    # Create a unique thread_id for every run to ensure fresh state
    config = {"configurable": {"thread_id": f"prod_test_{unique_id}"}}
    
    print(f"\n[STEP 1]: Initial User Input -> {user_input}")
    state = await graph.ainvoke({"messages": [("user", user_input)]}, config)
    
    # Check if Assistant needs more info (it shouldn't, since we provided everything)
    if state['messages'] and state['messages'][-1].type == "ai":
        print(f"[ASSISTANT]: {state['messages'][-1].content}")

    # 3. Check for HITL (Review Gate)
    snapshot = await graph.aget_state(config)
    if "Review_Gate" in snapshot.next:
        print("\n--- 🛑 HITL: PAUSED AT REVIEW GATE ---")
        extracted = snapshot.values.get('extracted_data', {})
        print(f"Extracted Data: {extracted}")
        
        # CHOICE: REJECT FIRST (Test the loop)
        # We only correct the AGE, leaving the dynamic email intact.
        print("\n[STEP 3]: Human Rejection (Correction)")
        print(">> User corrects: 'Actually, my age is 35'")
        
        await graph.aupdate_state(config, {
            "messages": [("user", "Actually, my age is 35")], 
            "is_approved": False 
        })
        # Resume -> goes back to Agent -> Inspector -> Review_Gate
        await graph.ainvoke(None, config)
        
        # 4. FINAL APPROVAL
        print("\n[STEP 4]: Human Approval (Final)")
        await graph.aupdate_state(config, {"is_approved": True})
        
        # This will trigger the SUBMITTER which calls the MCP SERVER
        print("Resuming graph to trigger MCP Submitter...")
        final_state = await graph.ainvoke(None, config)
        
        print("\n" + "="*50)
        print("FINAL PRODUCTION RESULT")
        print("="*50)
        last_msg = final_state['messages'][-1].content
        print(f"Last Message: {last_msg}")
        print(f"Final Data in State: {final_state.get('extracted_data')}")
        
        if "Success" in str(last_msg):
            print("\n✅ TEST PASSED: Data successfully submitted to MCP Server.")
        else:
            print("\n❌ TEST FAILED: Backend returned an error.")

if __name__ == "__main__":
    asyncio.run(run_test())