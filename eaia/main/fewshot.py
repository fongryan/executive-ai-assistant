"""Fetches few shot examples for triage step."""

from langgraph.store.base import BaseStore
from eaia.schemas import EmailData


template = """Email Subject: {subject}
Email From: {from_email}
Email To: {to_email}
Email Content: 
```
{content}
```
> Triage Result: {result}"""


def format_similar_examples_store(examples):
    strs = ["Here are some previous examples:"]
    for eg in examples:
        strs.append(
            template.format(
                subject=eg.value["input"]["subject"],
                to_email=eg.value["input"]["to_email"],
                from_email=eg.value["input"]["from_email"],
                content=eg.value["input"]["page_content"][:400],
                result=eg.value["triage"],
            )
        )
    return "\n\n------------\n\n".join(strs)


async def get_few_shot_examples(email: EmailData, store: BaseStore, config):
    import asyncio
    import os
    import tempfile
    
    # Handle the tiktoken blocking issue by preparing the environment
    # before making any search requests
    
    # Create a wrapper function to perform the actual search
    async def perform_search():
        namespace = (
            config["configurable"].get("assistant_id", "default"),
            "triage_examples",
        )
        try:
            # Define the synchronous operation that might cause blocking
            def sync_search_operation():
                # Pre-calculate and set the environment variables that tiktoken needs
                # to avoid os.getcwd() being called in an async context
                cwd = os.getcwd()
                temp_dir = os.path.join(tempfile.gettempdir(), "data-gym-cache")
                os.makedirs(temp_dir, exist_ok=True)
                os.environ["TIKTOKEN_CACHE_DIR"] = temp_dir
                return None  # Just setup, no actual search here
            
            # Run potentially blocking setup in a thread
            await asyncio.to_thread(sync_search_operation)
            
            # Now that environment is set up, do the actual search
            return await store.asearch(namespace, query=str({"input": email}), limit=5)
        except Exception as e:
            print(f"Error in search operation: {str(e)}")
            return None
    
    # Execute the search with proper async handling
    result = await perform_search()
    
    if result is None:
        return ""
    return format_similar_examples_store(result)
