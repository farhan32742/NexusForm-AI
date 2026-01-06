import asyncio
import sys
import time
import os
from dotenv import load_dotenv, find_dotenv

# Ensure the app can find the 'src' folder
sys.path.append(os.path.join(os.getcwd(), "src"))
# Ensure we can find 'shared_core' (2 levels up from apps/agent_app)
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..", "..")))

from src.agenticAI_full_workflow.agent.agent_workflow import AgentWorkflowBuilder

# Load .env from project root (or wherever it is found up the tree)
load_dotenv(find_dotenv(), override=True)

# Helper for async input to prevent blocking the event loop
async def ainput(prompt: str = "") -> str:
    return await asyncio.to_thread(input, prompt)

async def run_interactive():
    print("==================================================")
    print("       INTERACTIVE AGENT WORKFLOW TEST CLI        ")
    print("==================================================")
    
    print("[INIT]: Building Agent Workflow...")
    builder = AgentWorkflowBuilder()
    graph = builder.build()
    
    # Generate a unique thread ID for this session
    current_time = int(time.time())
    thread_id = f"interactive_session_{current_time}"
    config = {"configurable": {"thread_id": thread_id}}
    print(f"[INIT]: Session ID: {thread_id}")
    
    # 1. Get Initial User Input
    print("\n--------------------------------------------------")
    print("STEP 1: INITIAL INPUT")
    print("Please provide the initial user information.")
    print("Examples:")
    print(" - 'My name is Ali, age 25, email ali@test.com'")
    print(" - 'My name is John, CNIC 12345...'")
    print("--------------------------------------------------")
    
    user_input = await ainput(">>> ")
    if not user_input.strip():
        print("[WARN]: Empty input provided. Using default test data.")
        user_input = f"My name is Interactive User {current_time}, age 30, email user{current_time}@test.com"
        print(f"[INFO]: Input set to: {user_input}")

    print("\n[SYSTEM]: Processing... (Scout -> Agent -> Inspector -> Review Gate)")
    
    # Initial Run
    # We pass 'is_approved': False explicitly to ensure we stop at the gate if configured to do so
    await graph.ainvoke(
        {"messages": [("user", user_input)], "is_approved": False}, 
        config
    )
    
    # Loop to handle the workflow state
    while True:
        snapshot = await graph.aget_state(config)
        
        # 1. CHECK IF EXECUTION FINISHED (Interviewer Mode OR Final Success)
        if not snapshot.next:
            last_msg = snapshot.values.get("messages", [])[-1]
            content = str(last_msg.content)
            
            # A. CHECK FOR SUCCESS (Submitter Node Result)
            # The submitter node typically says "Success: Data for X saved" or "Backend Error"
            if "Success" in content or "saved" in content.lower():
                 print("\n==================================================")
                 print("                WORKFLOW COMPLETED                ")
                 print("==================================================")
                 print(f"[FINAL MESSAGE]: {content}")
                 print(f"[FINAL DATA]: {snapshot.values.get('extracted_data')}")
                 break
            
            # B. CHECK FOR FAILURE/ERROR
            if "Error" in content and "Backend" in content:
                 print("\n[ERROR]: Backend returned an error.")
                 print(f"[DETAILS]: {content}")
                 print("\n[SYSTEM]: You can try to provide corrected data (e.g. 'retry with email X').")
            
            # C. INTERVIEWER MODE (Agent needs more info)
            # If not success/error, it's the Agent asking a question
            print(f"\n[ASSISTANT]: {content}")
            
            user_reply = await ainput("\n>>> ")
            if user_reply.lower() in ["q", "quit", "exit"]:
                 print("[SYSTEM]: Exiting.")
                 break
                 
            # Continue conversation
            print("[SYSTEM]: Sending reply to Agent...")
            await graph.ainvoke({"messages": [("user", user_reply)]}, config)
            continue

        # 2. CHECK IF PAUSED AT REVIEW GATE
        if "Review_Gate" in snapshot.next:
            print("\n--------------------------------------------------")
            print("🛑 STEP: HUMAN REVIEW GATE")
            print("--------------------------------------------------")
            
            extracted = snapshot.values.get('extracted_data', {})
            print(f"Extracted Data: {extracted}")
            
            print("\n[OPTIONS]:")
            print(" [1] Approve & Submit")
            print(" [2] Reject & Correct (Provide feedback)")
            print(" [q] Quit")
            
            choice = await ainput("\nSelect Option [1/2/q]: ")
            
            if choice == "1":
                print("\n[ACTION]: Approving data...")
                # Update state to approved
                await graph.aupdate_state(config, {"is_approved": True})
                
                print("[SYSTEM]: Resuming workflow (Proceeding to Submitter)...")
                await graph.ainvoke(None, config)
                
            elif choice == "2":
                print("\n[ACTION]: Rejecting data.")
                feedback = await ainput("Enter your correction/feedback: ")
                
                if not feedback.strip():
                    feedback = "Please double check the data."
                
                print(f"[SYSTEM]: Sending feedback to Agent: '{feedback}'")
                
                # Update state with new message and ensure approved is False
                await graph.aupdate_state(config, {
                    "messages": [("user", feedback)],
                    "is_approved": False
                })
                
                print("[SYSTEM]: Resuming workflow (Back to Agent)...")
                await graph.ainvoke(None, config)
                
            elif choice.lower() == "q":
                print("[SYSTEM]: Exiting interactive session.")
                break
            else:
                print("[ERROR]: Invalid choice. Please try again.")
                continue
                
        else:
            # If paused somewhere else (unexpected for this specific flow, but possible)
            print(f"\n[SYSTEM]: Paused at unexpected node: {snapshot.next}")
            print("Resuming...")
            await graph.ainvoke(None, config)

if __name__ == "__main__":
    try:
        asyncio.run(run_interactive())
    except KeyboardInterrupt:
        print("\n\n[SYSTEM]: Test script interrupted by user.")