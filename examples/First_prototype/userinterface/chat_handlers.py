from EchoMind.engines.llm import LLMEngine
from EchoMind.managers.xml_manager import get_user_profile, reset_dynamic

from EchoMind.engines.rag import RAGSystem
from EchoMind.utils.helpers import setup_openai_key
from pathlib import Path

# Initialize with demo-specific paths
current_dir = Path(__file__).parent
docs_path = current_dir.parent / "docs"
index_path = current_dir.parent / "faiss_index"

# Set up OpenAI key from demo config
setup_openai_key(current_dir / "config.json")

# Create RAG system
rag = RAGSystem(
    docs_path=str(docs_path),
    index_path=str(index_path)
)
rag.build_or_update_index()

def handle_query(query):
    return rag.retrieve_content(query)

llm_class = LLMEngine(rag_system=rag)
def update_chat_history(user_message, chat_history, username):
    system_response = llm_class.generate_llm_response(username, user_message, session_history=chat_history, mode="standard")
    updated_history = chat_history + [[f"👤 {user_message}", f"🤖 {system_response}"]]
    profile = get_user_profile(username, mode="standard")
    session_history_text = ""
    for turn in updated_history:
        session_history_text += f"{turn[0]}\n{turn[1]}\n\n"
    dashboard_text = (
        f"User Profile:\n"
        f"  - Expertise: {profile['expertise']}\n"
        f"  - Time Available: {profile['time_available']}\n"
        f"  - Content Bias: {profile['content_bias']}\n"
        f"  - Predicted Mental State: {profile['mental_state']}\n"
        f"  - User Dialogue Bias: {profile['dialogue_bias']}\n\n"
        "Current Session Chat History:\n" + session_history_text
    )
    return updated_history, "", updated_history, dashboard_text

def new_chat_standard(username):
    if not username:
        return [], "Error: No user logged in.", []
    reset_dynamic(username, mode="standard")
    profile = get_user_profile(username, mode="standard")
    dashboard_text = (
        f"User Profile:\n"
        f"  - Expertise: {profile['expertise']}\n"
        f"  - Time Available: {profile['time_available']}\n"
        f"  - Content Bias: {profile['content_bias']}\n"
        f"  - Predicted Mental State: {profile['mental_state']}\n"
        f"  - User Dialogue Bias: {profile['dialogue_bias']}\n\n"
        "Current Session Chat History:\n"
    )
    return [], dashboard_text, []

def update_chat_history_file(user_message, file_chat_history, username, file_context):
    system_response = llm_class.generate_llm_response_file(username, user_message, file_context, session_history=file_chat_history, mode="file")
    updated_history = file_chat_history + [[f"👤 {user_message}", f"🤖 {system_response}"]]
    profile = get_user_profile(username, mode="file")
    session_history_text = ""
    for turn in updated_history:
        session_history_text += f"{turn[0]}\n{turn[1]}\n\n"

    dashboard_text = (
        f"User Profile:\n"
        f"  - Expertise: {profile['expertise']}\n"
        f"  - Time Available: {profile['time_available']}\n"
        f"  - Predicted Mental State: {profile['mental_state']}\n"
        f"  - User Dialogue Bias: {profile['dialogue_bias']}\n\n"
        "Current Session Chat History:\n" + session_history_text
    )
    return updated_history, "", updated_history, dashboard_text

def new_chat_file(username):
    if not username:
        return [], "Error: No user logged in.", []
    reset_dynamic(username, mode="file")
    profile = get_user_profile(username, mode="file")

    dashboard_text = (
        f"User Profile:\n"
        f"  - Expertise: {profile['expertise']}\n"
        f"  - Time Available: {profile['time_available']}\n"
        f"  - Predicted Mental State: {profile['mental_state']}\n"
        f"  - User Dialogue Bias: {profile['dialogue_bias']}\n\n"
        "Current Session Chat History:\n"
    )
    return [], dashboard_text, []

