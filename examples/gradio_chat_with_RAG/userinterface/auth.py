import json
import os
from EchoMind import ProfileManager
from EchoMind import XmlManager
from pathlib import Path
from icecream import ic
# Initialize with demo-specific paths
current_dir = Path(__file__).parent
user_schema_config_path = current_dir.parent / "user_schema_config.json"
xml_class = XmlManager(user_schema_config_path)
profile_class = ProfileManager(user_schema_config_path)
CREDENTIALS_FILE = "generated_data/credentials.json"

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_credentials(credentials):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f)

def signup(username, password):
    credentials = load_credentials()
    if username in credentials:
        return "Username already exists. Please choose another.", None
    
    credentials[username] = password
    save_credentials(credentials)
    
    # Get default profile with all schema fields
    default_profile = profile_class.predict_default_profile()
    ic("auth", default_profile)
    
    # Initialize user XML with full profile data
    xml_class.initialize_user_xml(
        user_id=username,
        profile_data=default_profile,
        content_bias="None",
        mode="standard"
    )
    
    return "Signup successful. Please log in with your new credentials.", None

def login(username, password):
    credentials = load_credentials()
    if username not in credentials:
        return "Username does not exist. Please sign up.", None
    if credentials[username] != password:
        return "Incorrect password.", None
    return f"Login successful. Welcome, {username}!", username