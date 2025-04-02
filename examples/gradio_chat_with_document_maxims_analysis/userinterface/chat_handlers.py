from EchoMind.engines.llm import LLMEngine
from EchoMind.managers.xml_manager import XmlManager
# from EchoMind.engines.rag import RAGSystem
from EchoMind.utils.helpers import setup_openai_key
from pathlib import Path
import json
from icecream import ic

# Initialize with demo-specific paths
current_dir = Path(__file__).parent
user_schema_config_path = current_dir.parent / "user_schema_config.json"

# Load schema configuration
with open(user_schema_config_path) as f:
    schema_config = json.load(f)
    schema_fields = sorted(schema_config["schema"].keys())

# Set up OpenAI key from demo config
setup_openai_key(current_dir / "config.json")

# # Create RAG system
# rag = RAGSystem(
#     docs_path=str(docs_path),
#     index_path=str(index_path)
# )
# rag.build_or_update_index()

xml_class = XmlManager(user_schema_config_path)

# def handle_query(query):
#     return rag.retrieve_content(query)

llm_class = LLMEngine(openai_config_path = current_dir / "config.json", schema_config_path=user_schema_config_path)

def _build_dashboard_text(profile):
    """Helper to build dynamic dashboard text based on schema"""
    profile_lines = ["User Profile:"]
    
    # Add schema fields
    for field in schema_fields:
        profile_lines.append(f"  - {field.replace('_', ' ').title()}: {profile.get(field, '')}")
    
    # Add static system fields
    system_fields = [
        # ("Content Evaluation", "content_maxim_evaluation"),
        ("Predicted Mental State", "mental_state"),
        ("LLM Dialogue Evaluation", "llm_dialogue_evaluation"),
    ]
    for label, key in system_fields:
        profile_lines.append(f"  - {label}: {profile.get(key, '')}")
    
    return "\n".join(profile_lines)

def update_chat_history_content_maxim_evaluation(user_message, file_chat_history, username, file_context, file_analysis):
    system_response, _ = llm_class.generate_llm_response_with_maxim_evaluation(username, user_message, file_context, file_analysis, session_history=file_chat_history, mode="file_maxim_evaluation")
    
    updated_history = file_chat_history + [[f"👤 {user_message}", f"🤖 {system_response}"]]
    profile = xml_class.get_user_profile_content_maxim_evaluation(username, mode="file_maxim_evaluation")

    session_history_text = ""
    for turn in updated_history:
        session_history_text += f"{turn[0]}\n{turn[1]}\n\n"
    
    dashboard_text = _build_dashboard_text(profile) + "\n\nCurrent Session Chat History:\n" + session_history_text
    return updated_history, "", updated_history, dashboard_text

def new_chat_file(username):
    if not username:
        return [], "Error: No user logged in.", []
    xml_class.reset_dynamic(username, mode="file_maxim_evaluation")
    profile = xml_class.get_user_profile_content_maxim_evaluation(username, mode="file_maxim_evaluation")
    dashboard_text = _build_dashboard_text(profile) + "\n\nCurrent Session Chat History:\n"
    return [], dashboard_text, []