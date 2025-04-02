
import openai
from openai import OpenAI
import json
from icecream import ic
from EchoMind.managers.xml_manager import XmlManager
from EchoMind.engines.rag import RAGSystem
from EchoMind.utils.helpers import setup_openai_key
from typing import List, Dict, Tuple, Optional



class LLMEngine:
    def __init__(self, openai_config_path: str = None,  rag_system: Optional[RAGSystem] = None, schema_config_path: Optional[str] = None):
        api_key = setup_openai_key(openai_config_path)
        self.client = openai.OpenAI(api_key=api_key)
        self.rag = rag_system
        self.schema_config_path = schema_config_path
        self.prompt_config = self._load_prompt_config()
        self.xml_class = XmlManager(self.schema_config_path)
        

        
    def _load_prompt_config(self):
        try:
            with open(self.schema_config_path, "r") as f:
                config = json.load(f)
            return config.get("prompt", {})
        except Exception as e:
            print(f"Error loading prompt config: {e}")
            return {}


    def predict_mental_state(self, user_input: str) -> str:
        """
        Function to predict the user's mental state using OpenAI's model.
        """
        try:
            # Define the system message to guide the model
            system_message = """
            You are an AI trained to predict the mental state of a user based on their input. 
            The possible mental states are:
            - Engaged (the user is interested and following along)
            - Curious (the user wants more info or deeper explanations)
            - Confused (the user is uncertain or not understanding)
            - Bored (the user’s attention is waning)
            - Frustrated (the user is annoyed or stuck)
            - Satisfied (the user feels their needs have been met)

            Analyze the user's input and predict the most likely mental state.
            Return only the predicted mental state as a single word.
            """

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # You can use "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3,  # Lower temperature for more deterministic output
                max_tokens=10     # Limit response length
            )

            # Extract and return the predicted mental state
            predicted_state = response.choices[0].message.content.strip()
            return predicted_state
        except Exception as e:
            return f"Error predicting mental state: {str(e)}"

    def predict_content_bias(self, text: str) -> str:
        """
        Function to predict bias in the retrieved content using OpenAI's model.
        """
        try:
            # Define the system message to guide the model
            # system_message = """
            # You are an AI trained to identify potential biases in text content. 
            # Analyze the provided text and identify any biases that may be present.
            # Return a concise list of the biases, if any or "Neutral" if no significant bias is detected.
            # """
            system_message = """You are an expert bias-detection AI. Analyze the given text and:
            1. Strictly list detected biases using ONLY short technical names (e.g., "Political bias", "Cultural bias")
            2. Use bullet points with "- " formatting
            3. Return "No biases detected" if none exist
            4. Never add explanations or descriptions

            Example output:
            - Confirmation bias
            - Gender bias"""

            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # You can use "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,  # Lower temperature for more deterministic output
                max_tokens=50     # Limit response length
            )

            # Extract and return the predicted bias
            predicted_bias = response.choices[0].message.content.strip()
            return predicted_bias
        except Exception as e:
            return f"Error predicting content bias: {str(e)}"


    def predict_dialogue_bias(self, text: str) -> str:
        """
        Function to predict bias in the user dialogue using OpenAI's model.
        """
        try:
            # Define the system message to guide the model
            # system_message = """
            # You are an AI trained to identify potential biases in user dialogue. 
            # Analyze the provided text and identify any biases that may be present.
            # Return a concise description of the bias or "Neutral" if no significant bias is detected.
            # """
            system_message = """You are an expert bias-detection AI. Analyze the given user dialogue and:
            1. Strictly list detected biases using ONLY short technical names (e.g., "Political bias", "Cultural bias")
            2. Use bullet points with "- " formatting
            3. Return "No biases detected" if none exist
            4. Never add explanations or descriptions

            Example output:
            - Confirmation bias
            - Gender bias"""
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # You can use "gpt-4" if you have access
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,  # Lower temperature for more deterministic output
                max_tokens=50     # Limit response length
            )

            # Extract and return the predicted bias
            predicted_bias = response.choices[0].message.content.strip()
            return predicted_bias
        except Exception as e:
            return f"Error predicting dialogue bias: {str(e)}"

        
    def generate_llm_response(self, user_id, user_input, session_history=None, mode="standard"):
        # Retrieve persistent dialogue history from XML (list of dicts with keys 'user' and 'system').
        persistent_history = self.xml_class.get_dialogue_history(user_id, mode)
        
        # Normalize persistent history to text.
        persistent_text = ""
        for turn in persistent_history:
            persistent_text += f"User: {turn.get('user', '')}\nAI: {turn.get('system', '')}\n"
        
        # Normalize current session history (if provided) to text.
        session_text = ""
        if session_history:
            for turn in session_history:
                # Here, each turn is assumed to be a list/tuple [user_msg, system_msg]
                session_text += f"{turn[0]}\n{turn[1]}\n"
                
        # Combine both histories.
        combined_history = persistent_text + "\n" + session_text

        # Retrieve user profile and dialogue history
        profile = self.xml_class.get_user_profile(user_id, mode)
        user_adaptation = [
        f"- **Mental State:** {profile['mental_state']}"
            ]
        # Build dynamic prompt sections
        for field, instructions in self.prompt_config.items():
            value = profile.get(field, "")
            user_adaptation.append(
                f"- **{field.replace('_', ' ').title()}:** {value}\n    {instructions}"
        )
        user_adaptation_text = "\n".join([
                "    " + line  # Add 4-space indentation to each line
                for entry in user_adaptation 
                for line in entry.split('\n')
            ])

        # Retrieve relevant content using the RAG module
        retrieved_content = self.rag.retrieve_content(session_text) if self.rag else ""

        # Predict biases
        content_bias_prediction = self.predict_content_bias(retrieved_content)
        dialogue_bias_prediction = self.predict_dialogue_bias(user_input)
        
        # Update XML with bias predictions
        self.xml_class.update_predicted_content_bias(user_id, content_bias_prediction, mode)
        

        # TODO: change the prompt for user-centric adaptation and also profile!
        system_prompt = f"""
            You are a conversational partner whose wisdom, intelligence, and empathy make your responses indistinguishable from a human's. Your primary goal is to provide precise, fact-based, and unbiased insights while engaging with users in a natural and human-like manner. In every interaction, consider the following guidelines:

            - **Grice's Maxims:**
            - **Quantity:** Offer just the right amount of information—neither too little nor too much.
            - **Quality:** Ensure every response is truthful and supported by accurate information.
            - **Relevance:** Stay on topic and address the user's query directly.
            - **Manner:** Communicate clearly and succinctly to avoid any confusion.

            - **Contextual Awareness:**
            - **Retrieved Content:** {retrieved_content}
            - **Combined History:** {combined_history}
            - **Bias Considerations:**
                - Content Bias: {content_bias_prediction}
                - Dialogue Bias: {dialogue_bias_prediction}

            - **User-Centric Adaptation:**
            {user_adaptation_text}

            Your responses should seamlessly integrate all of the above, ensuring that each interaction is both precise and warmly human.
            """
        
        # Use the new interface: explicitly import and use ChatCompletion.create()
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Update mental state and dialogue history
        new_state = self.predict_mental_state(user_input)
        self.xml_class.update_dynamic_mental_state(user_id, new_state, mode)
        self.xml_class.append_dialogue(user_id, user_input, reply, mode)
        self.xml_class.update_predicted_user_dialogue_bias(user_id, dialogue_bias_prediction, mode)
        return reply

    def generate_llm_response_file(self, user_id, user_input, file_analysis, session_history=None, mode="file"):
        persistent_history = self.xml_class.get_dialogue_history(user_id, mode)
        persistent_text = ""
        for turn in persistent_history:
            persistent_text += f"User: {turn.get('user', '')}\nAI: {turn.get('system', '')}\n"
        session_text = ""
        if session_history:
            for turn in session_history:
                session_text += f"{turn[0]}\n{turn[1]}\n"
        combined_history = persistent_text + "\n" + session_text

        profile = self.xml_class.get_user_profile(user_id, mode)
        dialogue_bias_prediction = self.predict_dialogue_bias(user_input)
        user_adaptation = [
        f"- **Mental State:** {profile['mental_state']}"
            ]
        # Build dynamic prompt sections
        for field, instructions in self.prompt_config.items():
            value = profile.get(field, "")
            user_adaptation.append(
                f"- **{field.replace('_', ' ').title()}:** {value}\n    {instructions}"
        )
        user_adaptation_text = "\n".join([
                "    " + line  # Add 4-space indentation to each line
                for entry in user_adaptation 
                for line in entry.split('\n')
            ])


        system_prompt = f"""
        You are a conversational partner whose wisdom, intelligence, and empathy make your responses indistinguishable from a human's. Your primary goal is to provide precise, fact-based, and unbiased insights while engaging with users in a natural and human-like manner. In every interaction, consider the following guidelines:

        - **Grice's Maxims:**
        - **Quantity:** Offer just the right amount of information—neither too little nor too much.
        - **Quality:** Ensure every response is truthful and supported by accurate information.
        - **Relevance:** Stay on topic and address the user's query directly.
        - **Manner:** Communicate clearly and succinctly to avoid any confusion.

        - **Contextual Awareness:**
        - **Retrieved Content:** {file_analysis}
        - **Combined History:** {combined_history}
        - **Bias Considerations:**
            - Dialogue Bias: {dialogue_bias_prediction}

        - **User-Centric Adaptation:**
        {user_adaptation_text}

        Your responses should seamlessly integrate all of the above, ensuring that each interaction is both precise and warmly human.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        new_state = self.predict_mental_state(user_input)

        self.xml_class.update_dynamic_mental_state(user_id, new_state, mode)
        self.xml_class.append_dialogue(user_id, user_input, reply, mode)
        self.xml_class.update_predicted_user_dialogue_bias(user_id, dialogue_bias_prediction, mode)
        return reply
    
    def analyze_grice_maxims(self, 
                             user_id: str,
        text: str,
        domain_context: str = "general",
        guidelines: Optional[Dict[str, str]] = None,
        mode: str = "file_maxim_evaluation",
    ) -> Dict:
        """
        Analyze input text against Grice's maxims (Quantity, Quality, Relevance, Manner) using GPT-4.

        Args:
            text (str): The input text to analyze.
            api_key (str): OpenAI API key for authentication.
            domain_context (str, optional): Context about the domain of the text (e.g., "medical", "casual"). Default: "general".
            guidelines (Dict[str, str], optional): Custom guidelines for evaluating specific maxims. 
                Example: {"quantity": "Should be concise for technical docs"}.
            model (str, optional): OpenAI model to use. Default: "gpt-4".
            temperature (float, optional): Sampling temperature (0-2). Lower = deterministic. Default: 0.0.

        Returns:
            Dict: Analysis result with scores (1-5) and explanations for each maxim.
                Example: {"quantity": {"score": 4, "explanation": "..."}, ...}

        Raises:
            ValueError: If text is empty or API key is invalid.
        """
        # Validate inputs
        if not text.strip():
            raise ValueError("Text cannot be empty.")

        # System message defining the task
        system_message = (
            "You are a linguistics expert analyzing text for adherence to Grice's Cooperative Principle maxims: "
            "Quantity (informative, not over/under), Quality (truthful, evidence-backed), "
            "Relevance (stays on-topic), and Manner (clear, orderly, unambiguous)."
        )

        # User prompt with text, domain context, and guidelines
        guidelines_str = ""
        if guidelines:
            guidelines_str = "\nCustom Guidelines:\n" + "\n".join(
                [f"- {maxim}: {desc}" for maxim, desc in guidelines.items()]
            )

        user_prompt = (
            f"Analyze this text for Grice's maxims:\n\n{text}\n\n"
            f"Domain Context: {domain_context}\n"
            f"{guidelines_str}\n\n"
            "Provide a JSON response with a numerical score (1-5) and concise explanation for each maxim. "
            "Example format: {\"quantity\": {\"score\": 3, \"explanation\": \"...\"}, ...}"
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}  # Ensure JSON output
            )
            analysis = json.loads(response.choices[0].message.content)
            self.xml_class.update_predicted_content_maxim_evaluation(user_id, analysis, mode)
            return analysis
        
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

    def analyze_grice_maxims_in_response(self, 
        conversation_history: List[Tuple[str, str]],  # [(user_msg, ai_response), ...]
        latest_response: str,
        domain_context: str = "general",
        guidelines: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Evaluate the LLM's latest response against Grice's maxims within conversation context.
        
        Args:
            conversation_history: Full dialogue history as list of (user, ai) tuples
            latest_response: The LLM response to evaluate
            api_key: OpenAI API key
            domain_context: Domain-specific context for evaluation
            guidelines: Custom evaluation criteria per maxim
            model: Model to use for evaluation
            temperature: Response randomness control
        
        Returns:
            Dict: Maxim evaluation with scores and explanations
        """
        if not conversation_history:
            raise ValueError("Conversation history cannot be empty")
        if not latest_response.strip():
            raise ValueError("LLM response cannot be empty")

        # Extract relevant context (last 3 exchanges for efficiency)
        # context_exchanges = "\n".join(
        #     [f"User: {u}\nAI: {a}" for u, a in conversation_history[-3:]]
        # )

        system_prompt = """You are a dialogue quality analyzer. Evaluate the AI's final response 
        in the provided conversation history against Grice's maxims, considering:\n
        1. How well it maintains Quantity given the conversation flow\n
        2. Truthfulness and evidence (Quality) based on available context\n
        3. Relevance to both immediate and broader dialogue context\n
        4. Clarity and structure (Manner) in the response"""

        user_prompt = f"""Conversation Context:\n{conversation_history}\n\nLatest AI Response:\n{latest_response}\n\n
        Domain: {domain_context}\nCustom Guidelines: {guidelines or 'None'}\n\n
        Provide JSON evaluation with 1-5 scores and explanations for each maxim."""

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"Evaluation failed: {str(e)}"}

    def generate_llm_response_with_maxim_evaluation(self,
        user_id: str,
        user_input: str,
        file_context: Optional[str] = None,
        file_analysis: Optional[str] = None,
        session_history: Optional[List[Tuple[str, str]]] = None,
        domain_context: str = "general",
        mode: str = "file_maxim_evaluation",
    ) -> Dict[str, str]:
        """
        Generate LLM response with integrated Grice's maxim evaluation
        
        Args:
            user_id: User identifier for history tracking
            user_input: Current user message
            api_key: OpenAI API key
            file_analysis: Optional content analysis from previous processing
            session_history: Current session's dialogue history
            domain_context: Domain context for response generation
            model: Model to use for generation
            max_tokens: Response length limit
            temperature: Creativity control
        
        Returns:
            Dict containing response text and maxim evaluation
        """
        # Get persistent history and construct prompt (implementation details would depend on storage system)
        persistent_history = self.xml_class.get_dialogue_history(user_id, mode)
        persistent_text = ""
        for turn in persistent_history:
            persistent_text += f"User: {turn.get('user', '')}\nAI: {turn.get('system', '')}\n"
        session_text = ""
        if session_history:
            for turn in session_history:
                session_text += f"{turn[0]}\n{turn[1]}\n"
        combined_history = persistent_text + "\n" + session_text
        # ic(combined_history)
        # Generate response using similar logic to reference code
        system_message = f"""You are a conversational AI. Follow these guidelines:
        - Grice's Maxims: Be informative but concise (Quantity), truthful (Quality), 
        relevant to conversation history, and clear (Manner)
        - Context: {file_context or 'No file context'}
        - Grice's maxim evaluation: {file_analysis or 'No file analysis'}
        - Domain: {domain_context}"""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=0.0
            )
            llm_response = response.choices[0].message.content.strip()

            new_state = self.predict_mental_state(user_input)

            self.xml_class.update_dynamic_mental_state(user_id, new_state, mode)
            self.xml_class.append_dialogue(user_id, user_input, llm_response, mode)
            # Evaluate the response
            maxim_evaluation = self.analyze_grice_maxims_in_response(
                conversation_history=combined_history,
                latest_response=llm_response,
                domain_context=domain_context,
            )

            self.xml_class.update_predicted_LLM_dialogue_maxim_evaluations(user_id, maxim_evaluation, mode)
            return llm_response,{
                "response": llm_response,
                "evaluation": maxim_evaluation,
                "history": combined_history
            }
            
        except Exception as e:
            return {"error": f"Response generation failed: {str(e)}"}

    