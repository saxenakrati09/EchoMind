import gradio as gr
from userinterface.auth import login, signup
from userinterface.profile_handlers import set_profile_callback
from userinterface.chat_handlers import (
    update_chat_history,
    new_chat_standard,
    update_chat_history_file,
    new_chat_file
)
from userinterface.museum_handlers import load_artworks, update_museum_chat, new_museum_chat
from userinterface.file_analysis import analyze_file_biases
from EchoMind.managers.xml_manager import get_user_profile




def login_action(username, password):
    msg, user = login(username, password)
    if user:
        profile = get_user_profile(user)
        return (
            msg,
            user,
            gr.update(visible=False),
            gr.update(visible=True),
            [],
            gr.update(value=profile["expertise"]),
            gr.update(value=profile["time_available"])
        )
    return (msg, "", gr.update(), gr.update(), None, gr.update(), gr.update())

# Add this CSS at the top of your Gradio Blocks definition
css = """
.artwork-tile {
    width: 95%;
    min-height: 150px;
    margin: 10px auto;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: flex;
    align-items: center;
    transition: transform 0.2s;
    background-color: white;
}

.artwork-tile:hover {
    transform: translateX(5px);
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.artwork-image-container {
    width: 120px;
    height: 120px;
    flex-shrink: 0;
    margin-right: 20px;
    background-color: #f5f5f5;
    border-radius: 4px;
    overflow: hidden;
}

.artwork-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.artwork-info {
    flex-grow: 1;
    padding-right: 20px;
}

.artwork-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
}

.artwork-artist {
    font-size: 14px;
    color: #666;
}

.select-button {
    width: 120px;
    padding: 8px 15px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s;
    flex-shrink: 0;
}

.select-button:hover {
    background-color: #45a049;
}
"""

with gr.Blocks(css=css) as demo:

    gr.Markdown("# EchoMind LLM Chat System")
    
    current_user = gr.State("")
    chat_history = gr.State([])
    file_context = gr.State("")
    file_chat_history = gr.State([])

    # Add new state variables
    museum_chat_history = gr.State([])
    current_artwork = gr.State({})
    show_museum_gallery = gr.State(True)
    
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
                    gr.Markdown("### Set Profile")
                    expertise_dropdown = gr.Dropdown(choices=["expert", "novice"], label="Expertise")
                    time_dropdown = gr.Dropdown(choices=["in a hurry", "not in a hurry"], label="Time Availability")
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

        with gr.Tab("File Content Chat"):
            with gr.Row():
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

        with gr.Tab("Museum Chat"):
            # Create empty columns first
            with gr.Column(visible=True) as museum_gallery_col:
                pass
                
            with gr.Column(visible=False) as museum_chat_col:
                pass
            
            # Fill gallery column
            with museum_gallery_col:
                gr.Markdown("## Select an Artwork")
                artworks = load_artworks()
                with gr.Column():  # Changed from Row to Column for vertical layout
                    for idx, artwork in enumerate(artworks):
                        with gr.Column(elem_classes=["artwork-tile"]):
                            with gr.Row():
                                # Image container
                                with gr.Column(elem_classes=["artwork-image-container"]):
                                    gr.Image(
                                        artwork["image"],
                                        elem_classes=["artwork-image"],
                                        show_label=False
                                    )
                                
                                # Artwork info
                                with gr.Column(elem_classes=["artwork-info"]):
                                    gr.Markdown(
                                        f"<div class='artwork-title'>{artwork['name']}</div>"
                                        f"<div class='artwork-artist'>by {artwork['painter']}</div>"
                                    )
                                
                                # Select button
                                with gr.Column():
                                    select_btn = gr.Button(
                                        "Select",
                                        elem_classes=["select-button"]
                                    )

                                    select_btn.click(
                                        lambda: gr.update(visible=False),
                                        inputs=[],
                                        outputs=[museum_gallery_col]
                                    ).then(
                                        lambda a=artwork: a,
                                        outputs=[current_artwork]
                                    ).then(
                                        lambda: gr.update(visible=True),
                                        outputs=[museum_chat_col]
                                    ).then(
                                        lambda: [],  # Clear chat history
                                        outputs=[museum_chat_history]
                                    )
                                
            # Fill chat column
            with museum_chat_col:
                with gr.Row():
                    gr.Button("← Back to Gallery").click(
                        lambda: (
                            gr.update(visible=True),
                            gr.update(visible=False),
                            None,
                            []
                        ),
                        outputs=[museum_gallery_col, museum_chat_col, current_artwork, museum_chat_history]
                    )
                with gr.Row():
                    # Left Column: Artwork Info
                    with gr.Column():
                        gr.Markdown("### Selected Artwork")
                        artwork_image = gr.Image(label="Artwork", interactive=False)
                        artwork_title = gr.Textbox(label="Title", interactive=False)
                        artwork_artist = gr.Textbox(label="Artist", interactive=False)
                    
                    # Middle Column: Chat
                    with gr.Column():
                        museum_chatbot = gr.Chatbot(label="Museum Chat")
                        museum_input = gr.Textbox(label="Your Message")
                        museum_chat_btn = gr.Button("Send")
                    
                    # Right Column: Dashboard
                    with gr.Column():
                        museum_dashboard = gr.Textbox(label="Dashboard Info", interactive=False)

                # PROPER INDENTATION FOR CHANGE HANDLER
                # Should be inside museum_chat_col but after component definitions
                current_artwork.change(
                    lambda a: (
                        a["image"] if a and "image" in a else "",
                        a["name"] if a and "name" in a else "",
                        a["painter"] if a and "painter" in a else "",
                        f"Artwork Selected: {a['name']} by {a['painter']}" if a else "Select an artwork to begin"
                    ),
                    inputs=[current_artwork],
                    outputs=[artwork_image, artwork_title, artwork_artist, museum_dashboard]
                )
        
    login_btn.click(
        login_action,
        inputs=[username_input, password_input],
        outputs=[login_output, current_user, login_page, main_interface, chat_history, expertise_dropdown, time_dropdown]
    )
    signup_btn.click(signup, inputs=[username_input, password_input], outputs=[login_output, current_user])
    profile_btn.click(
        set_profile_callback,
        inputs=[expertise_dropdown, time_dropdown, current_user],
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
    analyze_btn.click(
        analyze_file_biases,
        inputs=[file_upload],
        outputs=[file_analysis_output, file_context]
    )
    file_chat_btn.click(
        update_chat_history_file,
        inputs=[file_chat_input, file_chat_history, current_user, file_context],
        outputs=[file_chatbot, file_chat_input, file_chat_history, file_dashboard_output]
    )
    new_file_chat_btn.click(
        new_chat_file,
        inputs=[current_user],
        outputs=[file_chatbot, file_dashboard_output, file_chat_history]
    )

    # Chat interactions
    museum_chat_btn.click(
        update_museum_chat,
        inputs=[museum_input, museum_chat_history, current_user, current_artwork],
        outputs=[museum_chatbot, museum_input, museum_chat_history, museum_dashboard]
    )
            
if __name__ == "__main__":
    demo.launch()
    