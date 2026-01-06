import asyncio
from dotenv import load_dotenv
from src.agenticAI_full_workflow.agent.agent_workflow import AgentWorkflowBuilder

load_dotenv()

async def run_test():
    builder = AgentWorkflowBuilder()
    graph = builder.build()
    
    # 1. FIRST RUN: Provide full data to reach the Gate
    user_input = "My name is Ali, age 25, CNIC 42201-1234567-1, email ali@test.com"
    config = {"configurable": {"thread_id": "hitl_test_99"}}
    
    print(f"\n[USER]: {user_input}")
    # Graph will run Scout -> Agent -> Inspector -> Review_Gate (PAUSE)
    await graph.ainvoke({"messages": [("user", user_input)], "is_approved": False}, config)

    # 2. CHECK IF PAUSED
    snapshot = await graph.aget_state(config)
    if "Review_Gate" in snapshot.next:
        print("\n--- GRAPH IS PAUSED FOR HUMAN REVIEW ---")
        print(f"Current Data: {snapshot.values['extracted_data']}")
        
        # CHOICE 1: REJECTION / EDIT
        # Let's simulate the human saying "Wait, age is actually 26"
        print("\n[HUMAN]: No, the age is 26. Fix it.")
        await graph.aupdate_state(config, {
            "messages": [("user", "The age is 26")], 
            "is_approved": False # Keep it False to loop back
        })
        
        # Resume -> it goes back to Agent (as per our re-edit edge)
        await graph.ainvoke(None, config)
        
        # CHOICE 2: ACCEPTANCE
        # Now let's assume the data is correct
        print("\n[HUMAN]: Everything looks good now. I approve.")
        await graph.aupdate_state(config, {"is_approved": True})
        
        # Resume -> it goes to Submitter
        final_state = await graph.ainvoke(None, config)
        print(f"\n[FINAL RESPONSE]: {final_state['messages'][-1].content}")

if __name__ == "__main__":
    asyncio.run(run_test())