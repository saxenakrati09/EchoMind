import json
import os
from EchoMind import predict_default_profile
from EchoMind import initialize_user_xml

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
    default_profile = predict_default_profile()
    initialize_user_xml(username, default_profile["expertise"], default_profile["time_available"], mode="standard")
    initialize_user_xml(username, default_profile["expertise"], default_profile["time_available"], mode="file")
    initialize_user_xml(username, default_profile["expertise"], default_profile["time_available"], mode="museum")
    return "Signup successful. Please log in with your new credentials.", None

def login(username, password):
    credentials = load_credentials()
    if username not in credentials:
        return "Username does not exist. Please sign up.", None
    if credentials[username] != password:
        return "Incorrect password.", None
    return f"Login successful. Welcome, {username}!", username