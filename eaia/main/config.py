import os
from pathlib import Path
import yaml
import asyncio
from functools import lru_cache
from typing import Dict, Any

# Import the async patch module to ensure blocking operations are handled properly
import eaia.async_patch

_ROOT = Path(__file__).absolute().parent


# @lru_cache(maxsize=1)
def get_config(config: dict) -> Dict[str, Any]:
    """Get configuration, either from configurable or from config.yaml.
    
    This function is cached to avoid repeated file operations when called multiple times.
    """
    # This loads things either ALL from configurable, or
    # all from the config.yaml
    # This is done intentionally to enforce an "all or nothing" configuration
    if "email" in config["configurable"]:
        return config["configurable"]
    else:
        with open(_ROOT.joinpath("config.yaml")) as stream:
            return yaml.safe_load(stream)


async def get_config_async(config: dict) -> Dict[str, Any]:
    """Async wrapper for get_config to prevent blocking operations.
    
    This ensures file operations are run in a separate thread when in an async context.
    """
    return await asyncio.to_thread(get_config, config)
