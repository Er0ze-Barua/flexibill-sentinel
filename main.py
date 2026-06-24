import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent import app

load_dotenv()

def extract_text_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list) and len(content) > 0:
        if isinstance(content[0], dict) and 'text' in content[0]:
            return content[0]['text']
    return str(content)

def main():
    print("====================================================")
    print("    FLEXIBILL SENTINEL: RECOVERY & DISPUTE ENGINE   ")
    print("====================================================")
    
    thread_id = input("Enter Thread ID (Session Name): ").strip()
    config = {"configurable": {"thread_id": thread_id}}
    
    email = input("Enter Customer Email to manage: ").strip()
    
    print(f"\n[System] Session '{thread_id}' active for target: {email}")
    print("Type your message below (or type 'exit' to quit):\n")
    
    initial_input = {
        "messages": [HumanMessage(content=f"System initialization notice: Managing account status for target client email: {email}")],
        "customer_email": email
    }
    
    output = app.invoke(initial_input, config=config)
    clean_resp = extract_text_content(output['messages'][-1].content)
    print(f"\nSentinel: {clean_resp}\n")
    
    while True:
        user_msg = input("You: ").strip()
        if user_msg.lower() == 'exit':
            print("Shutting down engine panel. Goodbye!")
            break
            
        if not user_msg:
            continue
            
        current_input = {"messages": [HumanMessage(content=user_msg)]}
        output = app.invoke(current_input, config=config)
        
        clean_resp = extract_text_content(output['messages'][-1].content)
        print(f"\nSentinel: {clean_resp}\n")

if __name__ == "__main__":
    main()