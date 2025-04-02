from EchoMind.managers.xml_manager import XmlManager
from EchoMind.managers.profile_manager import ProfileManager
from pathlib import Path
import json

# Initialize with schema config
current_dir = Path(__file__).parent
user_schema_config_path = current_dir.parent / "user_schema_config.json"

# Load schema to get field names
with open(user_schema_config_path) as f:
    schema_config = json.load(f)
    schema_fields = sorted(schema_config["schema"].keys())

xml_manager = XmlManager(user_schema_config_path)
profile_manager = ProfileManager(user_schema_config_path)
CREDENTIALS_FILE = "generated_data/credentials.json"

def set_profile_callback(*args):
    """
    Updated to handle dynamic number of schema fields
    args structure: [field1_value, field2_value, ..., username]
    """
    if len(args) < 1:
        return "Error: Invalid arguments"
    
    # Last argument is username
    username = args[-1]
    if not username:
        return "Error: No user logged in."
    
    # Create profile dictionary from schema fields
    profile_data = {}
    for i, field in enumerate(schema_fields):
        if i < len(args)-1:  # Exclude username
            profile_data[field] = args[i]
    
    # Update both XML and global profiles
    xml_manager.update_static_profile(username, profile_data)
    profile_manager.update_global_profiles(profile_data)
    
    # Generate success message
    details = ", ".join([f"{k.replace('_', ' ').title()}: {v}" for k,v in profile_data.items()])
    return f"Profile updated for {username}: {details}"