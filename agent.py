import os
from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from database import pool, get_customer_profile

load_dotenv()


class BillingState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    customer_email: str
    current_tier: str
    escalation_reason: str    


@tool
def lookup_customer(email: str) -> dict:
    """Looks up customer profile, subscription status, and billing metrics."""
    profile = get_customer_profile(email)
    if not profile:
        return {"error": "No customer found with that email."}
    return profile

@tool
def resolve_past_due_billing(user_id: int) -> str:
    """Updates the user's subscription status back to 'Active' and clears failed counts."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE subscriptions SET status = 'Active', failed_attempts_count = 0 WHERE user_id = %s;",
                (user_id,)
            )
            cur.execute(
                "UPDATE billing_history SET payment_status = 'Paid' WHERE user_id = %s AND payment_status = 'Failed';",
                (user_id,)
            )
    return f"Success: User {user_id} subscription set to Active and invoices marked Paid."

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

billing_tools = [lookup_customer, resolve_past_due_billing]
llm_with_tools = llm.bind_tools(billing_tools)

def billing_agent(state: BillingState):
    print("--- Billing Agent Processing ---")
    
    system_instruction = (
        "You are FlexiBill Sentinel, an automated billing recovery agent.\n"
        "Your goal is to handle subscription billing inquiries and payment failures.\n"
        "1. ALWAYS run lookup_customer first using the user's email to inspect their status.\n"
        "2. If the user is VIP and their subscription is 'Past_Due', you are authorized to run "
        "resolve_past_due_billing automatically to help them.\n"
        "3. If the user is Standard tier and has failed_attempts >= 2, you CANNOT clear it automatically. "
        "Stop and inform them their account requires manual management."
    )
    
    messages = [{"role": "system", "content": system_instruction}] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: BillingState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


builder = StateGraph(BillingState)

builder.add_node("agent", billing_agent)
builder.add_node("tools", ToolNode(billing_tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

from psycopg import Connection
def get_checkpointer(conn_string: str):
    conn = Connection.connect(conn_string, autocommit=True)
    checkpointer = PostgresSaver(conn)
    checkpointer.setup()
    return checkpointer

db_url = os.getenv("DATABASE_URL")
postgres_checkpointer = get_checkpointer(db_url)
app = builder.compile(checkpointer=postgres_checkpointer)