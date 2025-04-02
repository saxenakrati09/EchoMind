# EchoMind

EchoMind is a powerful, AI-driven conversational framework designed to enable conscious, personalized, and human-like interactions. Built to work with OpenAI API or RAG-based systems, EchoMind tailors responses based on a user's profile—incorporating custom profiles given by the admins (for example, user's expertise, available time, preferred details, type of conversation and more.)

=============
### Key Features
- Profile-Aware Conversations – Generates responses aligned with user expertise, preferences, and constraints.

- Conscious Communication – Ensures responses are contextually aware and human-like.

- Seamless Integration – Works effortlessly with OpenAI API or RAG architectures.

- Adaptive & Dynamic – Adjusts in real-time to provide meaningful, engaging dialogues.

- Scalable & Modular – Easily extendable for various applications, from personal assistants to enterprise chat solutions.

=============
For installing, clone this repository, go to the root folder

`>> cd EchoMind`
`>> pip install -e .`

Currently, the demos are available in examples folder.

For project admin:
Add a config.json with your openai key in your demo folder. (Currently only OpenAI API is supported)
Add user schema and their respective prompts (on how the LLM should behave in different user schemas) in user_schema_config.json (see examples)



=============
## TODO:
<s>1. Handle config</s>
<s>2. Add flexible schema design from admin</s>
<s>3. Implement RAG on projects documents</s>
4. Implement interfacing with chatbots
    + Gradio chatbot <- in progress
    + Flask chatbot
    + Other platform?
5. Implement document analysis (separately)
    + Gradio chatbot <- in progress
    + Flask chatbot
    + Other platform?
6. Implement integrations: with multimodal predictions
7. Implement online and external validations
8. Implement Ethics by Design
9. Implement data handling efficiently 
10. Add other API integrations




## Pre-requisites

1. The EchoMind library can be integreated into a chatbot. The chatbot ideally should contain a way to set user schema. For this, set default user schemas in user_schema_config.json in your project.
The user_schema_config.json would be used to create the selection panel for the user schema in the chatbot. 
2. The EchoMind library keeps track of the user chat session. For this, there should be unique user identifiers and session identifiers for each user.

### Citation

If you use EchoMind in your research or projects, please consider citing as follows:

@misc{EchoMind,
  author = {Krati Saxena},
  title = {EchoMind},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/saxenakrati09/EchoMind}},
}
