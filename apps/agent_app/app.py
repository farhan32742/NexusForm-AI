import asyncio
import uuid
from dotenv import load_dotenv
from src.agenticAI_full_workflow.agent.agent_workflow import AgentWorkflowBuilder

load_dotenv()

async def main():
    builder = AgentWorkflowBuilder()
    graph = builder.build()
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    print("\n🚀 Form-Agent is Online. (Type 'exit' to stop)")
    print("------------------------------------------")

    while True:
        # Check current state to see if we are waiting for a Review
        snapshot = await graph.aget_state(config)
        
        # --- IF WE ARE AT THE REVIEW GATE ---
        if snapshot.next and "Review_Gate" in snapshot.next:
            user_input = input("\n[USER (Review)]: ").strip()
            
            if user_input.lower() in ["exit", "quit"]: break
            
            # Logic: If user says 'yes', update state and RESUME
            if user_input.lower() in ["yes", "ok", "yup", "approve", "correct"]:
                print("--- [SYSTEM]: Approval received. Proceeding to submission... ---")
                # 1. Manually set is_approved to True
                await graph.aupdate_state(config, {"is_approved": True})
                # 2. Resume the graph by passing None as the input
                async for event in graph.astream(None, config, stream_mode="updates"):
                    pass
            else:
                # Logic: If user says anything else, treat as correction and RE-RUN from start
                print(f"--- [SYSTEM]: Correction received. Re-processing... ---")
                await graph.aupdate_state(config, {"is_approved": False})
                async for event in graph.astream({"messages": [("user", user_input)]}, config, stream_mode="updates"):
                    pass
        
        # --- IF WE ARE NOT AT REVIEW (Normal extraction/interview) ---
        else:
            user_input = input("\n[USER]: ")
            if user_input.lower() in ["exit", "quit"]: break

            async for event in graph.astream({"messages": [("user", user_input)]}, config, stream_mode="updates"):
                pass

        # Check state again after the run
        new_snapshot = await graph.aget_state(config)
        
        # Show Summary Table if we just hit the Review Gate
        if new_snapshot.next and "Review_Gate" in new_snapshot.next:
            data = new_snapshot.values.get("extracted_data", {})
            print("\n" + "="*40)
            print("📋  FORM SUMMARY FOR YOUR REVIEW")
            print("-" * 40)
            for key, val in data.items():
                print(f" {key.replace('_', ' ').title():<15}: {val}")
            print("="*40)
            print("👉 Is this correct? (Type 'Yes' to submit, or tell me what to fix)")
            continue

        # Finish if Submitter was reached
        if not new_snapshot.next:
            last_msg = new_snapshot.values["messages"][-1].content
            print(f"\n[ASSISTANT]: {last_msg}")
            if "Acceptance confirmed" in last_msg or "Successfully" in last_msg:
                print("\n--- Mission Accomplished ---")
                break

if __name__ == "__main__":
    asyncio.run(main())