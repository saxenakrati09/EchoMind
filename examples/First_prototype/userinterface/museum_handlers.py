import os
from EchoMind.engines.llm import LLMEngine
from EchoMind.managers.xml_manager import get_user_profile, reset_dynamic


MUSEUM_DATA_DIR = "museum_data"
llm_class = LLMEngine()
def load_artworks():
    artworks = []
    for filename in os.listdir(MUSEUM_DATA_DIR):
        if filename.endswith(".png"):
            base_name = filename[:-4]
            parts = base_name.split("_")
            
            # Check if the filename follows the expected pattern
            if len(parts) >= 4 and parts[0] == "artworkname" and "paintername" in parts:
                # Find the index where "paintername" starts
                painter_index = parts.index("paintername")
                
                # Extract artwork name and painter name
                artwork_name = " ".join(parts[1:painter_index])
                painter_name = " ".join(parts[painter_index+1:])

                # Check if the corresponding text file exists
                txt_file = os.path.join(MUSEUM_DATA_DIR, f"{base_name}.txt")
                if os.path.exists(txt_file):
                    with open(txt_file, "r") as f:
                        description = f.read()
                    
                    # Append the artwork data to the list
                    artworks.append({
                        "image": os.path.join(MUSEUM_DATA_DIR, filename),
                        "name": artwork_name,
                        "painter": painter_name,
                        "description": description
                    })
    return artworks

def update_museum_chat(user_message, chat_history, username, artwork_context):
    system_response = llm_class.generate_llm_response_museum(
        username, 
        user_message, 
        session_history=chat_history,
        mode="museum",
        context=artwork_context["description"]
    )
    updated_history = chat_history + [[f"👤 {user_message}", f"🤖 {system_response}"]]
    
    profile = get_user_profile(username, mode="museum")
    session_history_text = "\n".join([f"{turn[0]}\n{turn[1]}" for turn in updated_history])

    dashboard_text = (
        f"Artwork Context:\n"
        f"  - Title: {artwork_context['name']}\n"
        f"  - Artist: {artwork_context['painter']}\n\n"
        f"User Profile:\n"
        f"  - Expertise: {profile['expertise']}\n"
        f"  - Time Available: {profile['time_available']}\n"
        f"  - Content Bias: {profile['content_bias']}\n"
        f"  - User Dialogue Bias: {profile['dialogue_bias']}\n\n"
        f"  - Predicted Mental State: {profile['mental_state']}\n\n"
        "Chat History:\n" + session_history_text
    )
    return updated_history, "", updated_history, dashboard_text

def new_museum_chat(username):
    if not username:
        return [], "Error: No user logged in.", []
    reset_dynamic(username, mode="museum")
    return [], "New museum chat started. Select an artwork to begin.", []