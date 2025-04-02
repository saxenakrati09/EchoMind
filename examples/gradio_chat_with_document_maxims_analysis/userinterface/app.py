import gradio as gr
import json
from icecream import ic
from userinterface.auth import login, signup
from userinterface.profile_handlers import set_profile_callback
from userinterface.chat_handlers import (
    update_chat_history_content_maxim_evaluation,
    new_chat_file
)
from userinterface.file_analysis import analyze_file_maxims
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
        profile = xml_class.get_user_profile(user, mode="file_maxim_evaluation")
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
    file_context = gr.State("")
    file_chat_history = gr.State([])
    
    with gr.Column(visible=True, elem_id="login_page") as login_page:
        gr.Markdown("## Login / Signup")
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        with gr.Row():
            login_btn = gr.Button("Login")
            signup_btn = gr.Button("Signup")
        login_output = gr.Textbox(label="Status", interactive=False)

    with gr.Tabs(visible=False, elem_id="main_interface") as main_interface:
        with gr.Tab("File Content Chat"):
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
                    gr.Markdown("#### Upload and Analyze File")
                    file_upload = gr.File(label="Upload a .txt file", file_types=[".txt"])
                    analyze_btn = gr.Button("Analyze File")
                    file_analysis_output = gr.HTML()
                with gr.Column():
                    gr.Markdown("#### Chat Based on File Content")
                    file_chatbot = gr.Chatbot(label="File Chat History")
                    file_chat_input = gr.Textbox(label="Your Message")
                    file_chat_btn = gr.Button("Send")
                    new_file_chat_btn = gr.Button("New Chat")
                with gr.Column():
                    gr.Markdown("#### Dashboard")
                    file_dashboard_output = gr.Textbox(label="File Chat Dashboard Info")


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
    analyze_btn.click(
        analyze_file_maxims,
        inputs=[current_user, file_upload],
        outputs=[file_analysis_output, file_context]
    )
    file_chat_btn.click(
        update_chat_history_content_maxim_evaluation,
        inputs=[file_chat_input, file_chat_history, current_user, file_context, file_analysis_output],
        outputs=[file_chatbot, file_chat_input, file_chat_history, file_dashboard_output]
    )

    new_file_chat_btn.click(
        new_chat_file,
        inputs=[current_user],
        outputs=[file_chatbot, file_dashboard_output, file_chat_history]
    )
    
            
if __name__ == "__main__":
    demo.launch()
    