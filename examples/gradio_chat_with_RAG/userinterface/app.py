import gradio as gr
import json
from userinterface.auth import login, signup
from userinterface.profile_handlers import set_profile_callback
from userinterface.chat_handlers import (
    update_chat_history,
    new_chat_standard
)
from icecream import ic
from EchoMind.managers.xml_manager import XmlManager
from pathlib import Path
# Initialize with demo-specific paths
current_dir = Path(__file__).parent
user_schema_config_path = current_dir.parent / "user_schema_config.json"
xml_class = XmlManager(user_schema_config_path)
# Load schema configuration
def load_schema_config():
    try:
        with open(user_schema_config_path, "r") as f:
            config = json.load(f)
        return config.get("schema", {})
    except Exception as e:
        print(f"Error loading schema config: {e}")
        return {}

schema = load_schema_config()

def login_action(username, password):
    msg, user = login(username, password)
    if user:
        profile = xml_class.get_user_profile(user)
        # Dynamically generate dropdown updates based on schema
        dropdown_updates = []
        for field in sorted(schema.keys()):
            dropdown_updates.append(gr.update(value=profile.get(field, "")))
        return (
            msg,
            user,
            gr.update(visible=False),
            gr.update(visible=True),
            [],
            *dropdown_updates
        )
    return (msg, "", gr.update(), gr.update(), None, *[gr.update()]*len(schema))

with gr.Blocks() as demo:

    gr.Markdown("# EchoMind LLM Chat System")
    
    current_user = gr.State("")
    chat_history = gr.State([])
    
    with gr.Column(visible=True, elem_id="login_page") as login_page:
        gr.Markdown("## Login / Signup")
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        with gr.Row():
            login_btn = gr.Button("Login")
            signup_btn = gr.Button("Signup")
        login_output = gr.Textbox(label="Status", interactive=False)

    with gr.Tabs(visible=False, elem_id="main_interface") as main_interface:
        with gr.Tab("Standard Chat"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Set Schema")
                    # Dynamically create dropdowns
                    dropdowns = []
                    for field in sorted(schema.keys()):
                        choices = schema[field]
                        dropdown = gr.Dropdown(
                            choices=choices,
                            label=field.replace("_", " ").title()
                        )
                        dropdowns.append(dropdown)
                    profile_btn = gr.Button("Update Profile")
                    profile_output = gr.Textbox(label="Profile Update Status")
                    new_chat_btn = gr.Button("New Chat")
                with gr.Column():
                    gr.Markdown("### Chat")
                    chatbot = gr.Chatbot(label="Chat History")
                    chat_input = gr.Textbox(label="Your Message")
                    chat_btn = gr.Button("Send")
                with gr.Column():
                    gr.Markdown("### Dashboard")
                    dashboard_output = gr.Textbox(label="Dashboard Info")

    login_btn.click(
        login_action,
        inputs=[username_input, password_input],
        outputs=[
            login_output, 
            current_user, 
            login_page, 
            main_interface, 
            chat_history, 
            *dropdowns
        ]
    )

    signup_btn.click(signup, inputs=[username_input, password_input], outputs=[login_output, current_user])
    profile_btn.click(
        set_profile_callback,
        inputs=[*dropdowns, current_user],
        outputs=profile_output
    )
    chat_btn.click(
        update_chat_history,
        inputs=[chat_input, chat_history, current_user],
        outputs=[chatbot, chat_input, chat_history, dashboard_output]
    )
    new_chat_btn.click(
        new_chat_standard,
        inputs=[current_user],
        outputs=[chatbot, dashboard_output, chat_history]
    )
    
            
if __name__ == "__main__":
    demo.launch()
    