from EchoMind.engines.llm import LLMEngine
from pathlib import Path
import json
from EchoMind.utils.helpers import setup_openai_key
# Initialize with demo-specific paths
current_dir = Path(__file__).parent
user_schema_config_path = current_dir.parent / "user_schema_config.json"

# Load schema configuration
with open(user_schema_config_path) as f:
    schema_config = json.load(f)
    schema_fields = sorted(schema_config["schema"].keys())

# Set up OpenAI key from demo config
setup_openai_key(current_dir / "config.json")

llm_class = LLMEngine(openai_config_path = current_dir / "config.json", schema_config_path=user_schema_config_path)

def analyze_file_biases(uploaded_file):
    if uploaded_file is None:
        return "No file uploaded.", ""
    with open(uploaded_file.name, "r") as f:
        content = f.read()
    sentences = content.split('.')
    html_output = "<div style='font-family: Arial, sans-serif; line-height:1.5;'>"
    
    for s in sentences:
        s = s.strip()
        if s:
            sentence = s if s.endswith('.') else s + '.'
            bias = llm_class.predict_content_bias(sentence)
            if bias != "Neutral":
                html_output += (
                    f'<p style="color: red; font-weight: bold;">'
                    f'{sentence} '
                    f'<span style="color:black; background-color: yellow; padding: 2px 4px; border-radius: 3px;">[{bias}]</span>'
                    f'</p>'
                )
            else:
                html_output += f"<p>{sentence}</p>"
    html_output += "</div>"
    return html_output, content
