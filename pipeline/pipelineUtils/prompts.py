import os
import json
from pipelineUtils.blob_functions import get_blob_content
import yaml
import logging

from configuration import Configuration
config = Configuration()

# Path to local prompts directory (relative to this file)
LOCAL_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), 'prompts')


def load_prompts_from_blob(prompt_file):
    """Load the prompt from YAML file in blob storage and return as a dictionary."""
    try:
        prompt_yaml = get_blob_content("prompts", prompt_file).decode('utf-8')
        prompts = yaml.safe_load(prompt_yaml)
        prompts_json = json.dumps(prompts, indent=4)
        prompts = json.loads(prompts_json) 
        return prompts
    except Exception as e:
        raise RuntimeError(f"Failed to load prompts file: {prompt_file} from blob storage. Prompt File should be a valid Blob path stored in the prompts container. Error: {e}")


def load_prompts_from_local():
    """Load prompts from local text files in the prompts directory."""
    try:
        prompts = {}
        
        # Load system prompt
        system_prompt_path = os.path.join(LOCAL_PROMPTS_DIR, 'system_prompt.txt')
        if os.path.exists(system_prompt_path):
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                prompts['system_prompt'] = f.read().strip()
        
        # Load user prompt
        user_prompt_path = os.path.join(LOCAL_PROMPTS_DIR, 'user_prompt.txt')
        if os.path.exists(user_prompt_path):
            with open(user_prompt_path, 'r', encoding='utf-8') as f:
                prompts['user_prompt'] = f.read().strip()
        
        # Load agent prompt (optional)
        agent_prompt_path = os.path.join(LOCAL_PROMPTS_DIR, 'agent_prompt.txt')
        if os.path.exists(agent_prompt_path):
            with open(agent_prompt_path, 'r', encoding='utf-8') as f:
                prompts['agent_prompt'] = f.read().strip()
        
        return prompts
    except Exception as e:
        raise RuntimeError(f"Failed to load prompts from local files: {e}")
    

def load_prompts():
    """Fetch prompts from blob storage or local files based on PROMPT_FILE setting."""
    prompt_file = config.get_value("PROMPT_FILE")
    
    if not prompt_file:
        raise ValueError("Environment variable PROMPT_FILE is not set.")
    
    if prompt_file == "local":
        prompts = load_prompts_from_local()
    else:
        # Default: treat as blob storage path (e.g., "prompts.yaml")
        prompts = load_prompts_from_blob(prompt_file)

    # Validate required fields
    required_keys = ["system_prompt", "user_prompt"]
    for key in required_keys:
        if key not in prompts:
            raise KeyError(f"Missing required prompt key: {key}")

    return prompts


def load_agent_prompt():
    """Load the agent prompt for agentic processing."""
    prompt_file = config.get_value("PROMPT_FILE")
    
    if not prompt_file:
        raise ValueError("Environment variable PROMPT_FILE is not set.")
    
    if prompt_file == "local":
        prompts = load_prompts_from_local()
    else:
        prompts = load_prompts_from_blob(prompt_file)
    
    if 'agent_prompt' in prompts:
        return prompts['agent_prompt']
    
    # Return None if agent_prompt not found (caller can use default)
    return None