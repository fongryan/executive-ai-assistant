from langchain_community.document_loaders import GoogleDriveLoader
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain_core.messages import HumanMessage

# Step 1: Set up Google Docs loader as a tool
def load_google_doc(document_id: str, credentials_path: str, token_path: str):
    """Loads the content of a Google Doc given its document_id."""
    loader = GoogleDriveLoader(
        document_ids=[document_id],
        credentials_path=credentials_path,
        token_path=token_path,
        file_loader_cls=None,  # Only needed for non-Google files
    )
    docs = loader.load()
    return docs[0].page_content if docs else "Document not found."

# Step 2: Register the loader as a tool for LangGraph
tools = [
    {
        "name": "load_google_doc",
        "description": "Load content from a Google Doc using its document ID.",
        "function": load_google_doc,
        "args_schema": {
            "document_id": str,
            "credentials_path": str,
            "token_path": str,
        }
    }
]

tool_executor = ToolExecutor(tools)

# Step 3: Define the agent node and tool node
def agent_node(state):
    # Example: always call the tool with hardcoded IDs for demo
    return {"tool": "load_google_doc", "tool_input": {
        "document_id": "YOUR_GOOGLE_DOC_ID",
        "credentials_path": "path/to/credentials.json",
        "token_path": "path/to/token.json"
    }}

def tool_node(state):
    # Execute the tool and add result to state
    result = tool_executor(state["tool"], state["tool_input"])
    state["result"] = result
    return state

# Step 4: Build the LangGraph workflow
workflow = StateGraph(dict)

workflow.add_node("agent", agent_node)
workflow.add_node("action", tool_node)

workflow.set_entry_point("agent")
workflow.add_edge("agent", "action")
workflow.add_edge("action", END)

workflow = workflow.compile()

# Step 5: Run the workflow
if __name__ == "__main__":
    initial_state = {}
    output = workflow.invoke(initial_state)
    print("Google Doc Content:")
    print(output.get("result"))
