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

llm_class = LLMEngine(openai_config_path=current_dir / "config.json", schema_config_path=user_schema_config_path)

def analyze_file_maxims(username, uploaded_file, domain_context="general", mode="file_maxim_evaluation"):
    if uploaded_file is None:
        return "No file uploaded.", ""
    
    with open(uploaded_file.name, "r") as f:
        content = f.read()
    
    # Analyze the entire content for Grice's maxims
    evaluation = llm_class.analyze_grice_maxims(username, content, domain_context=domain_context, mode=mode)

    # Format evaluation as plain text
    evaluation_text = ""
    for maxim, details in evaluation.items():
        evaluation_text += (
            f"{maxim.capitalize()}:\n"
            f"  Score: {details['score']}\n"
            f"  Explanation: {details['explanation']}\n\n"
        )
        
    # Build HTML output: show file content followed by the evaluation
    html_output = "<div style='font-family: Arial, sans-serif; line-height:1.5;'>"
    html_output += "<h2>File Content</h2>"
    html_output += f"<p>{content}</p>"
    html_output += "<h2>Grice Maxims Evaluation</h2>"
    # html_output += f"<pre>{json.dumps(evaluation, indent=2)}</pre>"
    html_output += f"<p>{evaluation_text}</p>"
    html_output += "</div>"
    
    return html_output, content
