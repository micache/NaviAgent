"""
Utility functions for agents
"""
import asyncio
from typing import Optional, Callable, Any


async def retry_on_timeout(
    func: Callable,
    max_retries: int = 3,
    timeout_delay: float = 2.0,
    *args,
    **kwargs
) -> Any:
    """
    Retry a function if it times out
    
    Args:
        func: The async function to retry
        max_retries: Maximum number of retries
        timeout_delay: Delay between retries in seconds
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        The result of the function
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            if "timeout" in error_msg or "timed out" in error_msg:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"[Retry] Attempt {attempt + 1} failed with timeout, retrying in {timeout_delay}s...")
                    await asyncio.sleep(timeout_delay)
                    continue
            raise e
    
    raise last_error
