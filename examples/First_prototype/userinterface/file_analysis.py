from EchoMind.engines.llm import LLMEngine

llm_class = LLMEngine()
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