"""
async_utils.py

Utility functions for ensuring proper async behavior in LangGraph nodes.
These utilities help prevent blocking operations from impacting health checks and performance.
"""
import asyncio
import functools
from typing import Any, Callable, Coroutine, TypeVar

T = TypeVar('T')
R = TypeVar('R')


def ensure_async(func: Callable[..., R]) -> Callable[..., Coroutine[Any, Any, R]]:
    """
    Decorator to ensure a function is async-compatible.
    - If the function is already async, it's returned as is
    - If it's a sync function, it's wrapped to execute in a thread pool
    
    This prevents blocking the event loop for LangGraph async operations.
    
    Usage:
        @ensure_async
        def my_potentially_blocking_function(...):
            ...
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return await asyncio.to_thread(func, *args, **kwargs)
    return wrapper


async def run_non_blocking(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a potentially blocking function in a non-blocking way.
    Useful for one-off calls that might block the event loop.
    
    Usage:
        result = await run_non_blocking(potentially_blocking_func, arg1, arg2, kwarg1=value)
    """
    return await asyncio.to_thread(func, *args, **kwargs)


def make_node_async_safe(node_func: Callable) -> Callable:
    """
    Wrap a LangGraph node function to ensure all its operations are async-safe.
    This helps prevent BlockingIOError in LangGraph deployments.
    
    Usage:
        @make_node_async_safe
        def my_langgraph_node(state, config, store):
            # This function can now contain sync operations safely
            ...
    """
    @functools.wraps(node_func)
    async def async_safe_node(*args, **kwargs):
        if asyncio.iscoroutinefunction(node_func):
            # If already async, just await it
            return await node_func(*args, **kwargs)
        else:
            # If sync, run in thread pool
            return await asyncio.to_thread(node_func, *args, **kwargs)
    
    return async_safe_node
