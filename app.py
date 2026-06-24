import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import app

# 1. Page Configuration & Styling
st.set_page_config(page_title="FlexiBill Sentinel", page_icon="🛡️", layout="centered")
st.title("🛡️ FlexiBill Sentinel")
st.subheader("Automated AI Billing Recovery & Dispute Engine")
st.markdown("---")

# 2. Sidebar Configuration for Quick Testing
st.sidebar.header("Execution Environment")
thread_id = st.sidebar.text_input("Session (Thread ID)", value="portfolio_session_1")
config = {"configurable": {"thread_id": thread_id}}

st.sidebar.markdown("### Quick-Select Test Profiles")
profile_choice = st.sidebar.radio(
    "Choose a seeded user profile:",
    ("VIP Client (Auto-Recovery)", "Standard Client (Guardrail Block)")
)

# Map choices back to our PostgreSQL seed data emails
email_mapping = {
    "VIP Client (Auto-Recovery)": "eroze@test.com",
    "Standard Client (Guardrail Block)": "john@test.com"
}
target_email = email_mapping[profile_choice]

st.sidebar.info(f"Targeting Database Context:\n`{target_email}`")

# 3. Session State Memory Management for Streamlit UI
if "previous_profile" not in st.session_state:
    st.session_state.previous_profile = profile_choice

# FIXED: If the operator switches profiles, wipe the memory clean
if st.session_state.previous_profile != profile_choice:
    st.session_state.chat_history = []
    st.session_state.previous_profile = profile_choice

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def extract_text_content(content) -> str:
    """Helper to safely extract string text out of Gemini's various return formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list) and len(content) > 0:
        if isinstance(content[0], dict) and 'text' in content[0]:
            return content[0]['text']
    return str(content)

# 4. Render Active Chat Feed
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# 5. Handle Live Messaging Inputs
if user_query := st.chat_input("Ask Sentinel about your account or bill..."):
    # Display human turn
    with st.chat_message("user"):
        st.write(user_query)
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    # Process agent graph step execution
    with st.chat_message("assistant"):
        with st.spinner("Sentinel analyzing billing matrices..."):
            # Injecting email context dynamically into state frame
            graph_input = {
                "messages": [HumanMessage(content=f"Context: {user_query} (Client: {target_email})")],
                "customer_email": target_email
            }
            output = app.invoke(graph_input, config=config)
            
            # Extract and display response text safely
            raw_response = output['messages'][-1].content
            clean_response = extract_text_content(raw_response)
            
            st.write(clean_response)
            st.session_state.chat_history.append(AIMessage(content=clean_response))