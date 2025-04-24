import os
from dotenv import load_dotenv
from langchain_googledrive.document_loaders import GoogleDriveLoader
from langchain_googledrive.tools.google_drive.tool import GoogleDriveSearchTool
from langchain_googledrive.utilities.google_drive import GoogleDriveAPIWrapper
from langchain_openai import OpenAI
from langchain.agents import AgentType, initialize_agent

# Load environment variables from .env
load_dotenv()

# Set your folder ID (from Google Drive URL, or use "root" for your home directory)
# folder_id = "1H5va5UuxrMDPZ5tB21_IrdatsguIRozE"
folder_id = "root"

credentials_path = os.environ.get("GOOGLE_ACCOUNT_FILE")
print(f"credentials path is {credentials_path}")

# Initialize the Google Drive search tool
tool = GoogleDriveSearchTool(
    api_wrapper=GoogleDriveAPIWrapper(
        folder_id=folder_id,
        num_results=2,  # number of results to fetch
        # template="gdrive-query-in-folder",  # search in document bodies
        credentials_path=credentials_path
    )
)

# (Optional) Use within an agent with an LLM
llm = OpenAI(temperature=0)

drive = GoogleDriveSearchTool(
            api_wrapper=GoogleDriveAPIWrapper(
                folder_id=folder_id,
                num_results=2,
                # template="gdrive-query-in-folder",
                credentials_path=credentials_path
            )
        )

print("^^ start drive invoke")
results = drive.invoke("Ryan")
print(results)
print("^^ end drive invoke")

tools = [
    drive
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
)

print("^^ start agent invoke")
# Run a query
result = agent.invoke("Ryan")
print(result)

print("^^ start loader invoke")
loader = GoogleDriveLoader(
    folder_id=folder_id,
    recursive=True,
)
print(loader)
docs = loader.load()
print(docs)
for doc in docs:
    print("---")
    print(doc.page_content.strip()[:60] + "...")
