import json
import os
from pathlib import Path
from typing import Optional
from icecream import ic

def setup_openai_key(config_path: Optional[Path] = None) -> str:
    """
    Load OpenAI API key from explicit config path or current working directory.
    """
    # Try explicit config path first
    if config_path and config_path.exists():
        with open(config_path, 'r') as file:
            config = json.load(file)
        api_key = config.get('openai_api_key')
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            return api_key
        raise ValueError(f"OpenAI API key not found in {config_path}")

    # Try current working directory config
    cwd_config = Path.cwd() / "config.json"
    if cwd_config.exists():
        with open(cwd_config, 'r') as file:
            config = json.load(file)
        api_key = config.get('openai_api_key')
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            return api_key
        raise ValueError(f"OpenAI API key not found in {cwd_config}")

    raise FileNotFoundError(
        "No valid OpenAI config found. "
        "Either provide an explicit config_path or place a config.json "
        "in the current working directory with an 'openai_api_key' field."
    )