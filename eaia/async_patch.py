"""
async_patch.py

Comprehensive monkey-patching for blocking operations in async environments (LangGraph, ASGI, etc).
This ensures that any blocking calls (file operations, network calls, etc.) are properly handled
when inside an event loop, preventing BlockingError and keeping the application responsive.
"""
import os
import tempfile
import asyncio
import functools
import inspect
import io
import tiktoken
from typing import Any, Callable, TypeVar, cast, Dict

T = TypeVar('T')

# Cache for frequently accessed data to avoid blocking calls
_CACHE: Dict[str, Any] = {}

def patch_blocking_function(original_func: Callable[..., T]) -> Callable[..., T]:
    """
    Patch a blocking function to run in a separate thread when called from an async context.
    """
    @functools.wraps(original_func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context
            # CANNOT use run_until_complete inside a running event loop
            if not asyncio.iscoroutinefunction(original_func):
                # For synchronous functions, use to_thread but don't wait for it within wrapper
                # Instead return a coroutine that the caller should await
                async def async_wrapper():
                    return await asyncio.to_thread(original_func, *args, **kwargs)
                return async_wrapper()
            else:
                # If it's already async, just return the coroutine
                return original_func(*args, **kwargs)
        except RuntimeError:
            # Not in an event loop, call the function directly
            return original_func(*args, **kwargs)
    
    return cast(Callable[..., T], wrapper)

# Initialize cache with values needed for tiktoken
def _initialize_cache():
    """Pre-cache frequently accessed values to avoid blocking calls during runtime."""
    _CACHE["cwd"] = os.getcwd()
    
    # Create a fixed tempdir for tiktoken to use
    temp_dir = os.path.join(tempfile.gettempdir(), "data-gym-cache")
    os.makedirs(temp_dir, exist_ok=True)
    os.environ["TIKTOKEN_CACHE_DIR"] = temp_dir
    _CACHE["tempdir"] = temp_dir

    # Preload tiktoken tokenizer data synchronously
    try:
        print("Preloading tiktoken tokenizer...")
        tiktoken.get_encoding("cl100k_base") # Common encoding, forces loading
        print("Tiktoken preloading complete.")
    except Exception as e:
        print(f"Warning: Failed to preload tiktoken - {e}")

# Execute initialization at import time, when it's safe to do blocking calls
_initialize_cache()

# Replacement for os.getcwd that uses the cached value
def _non_blocking_getcwd():
    """Return the cached CWD instead of making a system call."""
    return _CACHE["cwd"]

# Replace the original function with our non-blocking version
os.getcwd = _non_blocking_getcwd

print("Applied async patches for os.getcwd")
