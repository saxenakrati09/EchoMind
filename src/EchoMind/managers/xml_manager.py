import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict
import json
from icecream import ic

class XmlManager:
    def __init__(self, schema_config_path: Optional[str] = None):
        if not schema_config_path:
            raise ValueError("schema_config_path is required")
        self.schema_config_path = schema_config_path
        self.schema_config = self._load_schema_config()
        
    def _load_schema_config(self) -> Dict:
        try:
            with open(self.schema_config_path, "r") as f:
                config = json.load(f)
            return config.get("schema", {})
        except Exception as e:
            print(f"Error loading schema config: {e}")
            return {}
        
    def get_user_xml_path(self, user_id: str, mode: str = "standard") -> str:
        return os.path.join("generated_data/users", f"{user_id}_{mode}.xml")

    def initialize_user_xml(self, user_id: str, profile_data: Dict[str, str], 
                          content_bias: str = "None", mode: str = "standard") -> None:
        path = self.get_user_xml_path(user_id, mode)
        if not os.path.exists("generated_data/users"):
            os.makedirs("generated_data/users")
        if not os.path.exists(path):
            root = ET.Element("ChatState")
            
            # Static layer
            static = ET.SubElement(root, "Static")
            user_profile = ET.SubElement(static, "UserProfile")
            for field in self.schema_config.keys():
                ET.SubElement(user_profile, field).text = profile_data.get(field, "")
            
            content_biases = ET.SubElement(static, "ContentBiases")
            ET.SubElement(content_biases, "Bias").text = content_bias
            
            # Dynamic layer
            dynamic = ET.SubElement(root, "Dynamic")
            ET.SubElement(dynamic, "DialogueHistory")
            mental_state = ET.SubElement(dynamic, "PredictedMentalState")
            ET.SubElement(mental_state, "State").text = "Neutral"
            pred_dialogue_bias = ET.SubElement(dynamic, "PredictedUserDialogueBias")
            ET.SubElement(pred_dialogue_bias, "Bias").text = "None"
            
            tree = ET.ElementTree(root)
            tree.write(path)
            
    def initialize_user_xml_file(self, user_id: str, profile_data: Dict[str, str], 
                          content_bias: str = "None", mode: str = "file") -> None:
        path = self.get_user_xml_path(user_id, mode)
        if not os.path.exists("generated_data/users"):
            os.makedirs("generated_data/users")
        if not os.path.exists(path):
            root = ET.Element("ChatState")
            
            # Static layer
            static = ET.SubElement(root, "Static")
            user_profile = ET.SubElement(static, "UserProfile")
            for field in self.schema_config.keys():
                ET.SubElement(user_profile, field).text = profile_data.get(field, "")

            content_biases = ET.SubElement(static, "ContentBiases")
            ET.SubElement(content_biases, "Bias").text = content_bias

            
            # Dynamic layer
            dynamic = ET.SubElement(root, "Dynamic")
            ET.SubElement(dynamic, "DialogueHistory")
            mental_state = ET.SubElement(dynamic, "PredictedMentalState")
            ET.SubElement(mental_state, "State").text = "Neutral"

            pred_dialogue_bias = ET.SubElement(dynamic, "PredictedUserDialogueBias")
            ET.SubElement(pred_dialogue_bias, "Bias").text = "None"
        
            tree = ET.ElementTree(root)
            tree.write(path)

    def initialize_user_xml_file_maxim_evaluation(self, user_id: str, profile_data: Dict[str, str], 
                          content_maxim_evaluation: str = "None", mental_state: str = "Neutral", 
                          llm_dialogue_evaluation: str = "None", mode: str = "file_maxim_evaluation") -> None:
        path = self.get_user_xml_path(user_id, mode)
        if not os.path.exists("generated_data/users"):
            os.makedirs("generated_data/users")
        if not os.path.exists(path):
            root = ET.Element("ChatState")
            
            # Static layer
            static = ET.SubElement(root, "Static")
            user_profile = ET.SubElement(static, "UserProfile")
            for field in self.schema_config.keys():
                ET.SubElement(user_profile, field).text = profile_data.get(field, "")

            content_maxim_evaluation = ET.SubElement(static, "ContentEvaluation")
            ET.SubElement(content_maxim_evaluation, "MaximEvaluation")
            
            # Dynamic layer
            dynamic = ET.SubElement(root, "Dynamic")
            ET.SubElement(dynamic, "DialogueHistory")
            mental_state = ET.SubElement(dynamic, "PredictedMentalState")
            ET.SubElement(mental_state, "State").text = "Neutral"
            llm_dialogue_evaluation = ET.SubElement(dynamic, "DialogueMaximEvaluation")
            llm_dialogue_evaluation.text = "None"

            
            tree = ET.ElementTree(root)
            tree.write(path)
            
    def update_static_profile(self, user_id: str, profile_data: Dict[str, str]) -> None:
        for mode in ["standard", "file"]:
            path = self.get_user_xml_path(user_id, mode)
            if os.path.exists(path):
                tree = ET.parse(path)
                root = tree.getroot()
                user_profile = root.find("./Static/UserProfile")
                
                for field in self.schema_config.keys():
                    element = user_profile.find(field)
                    if element is not None:
                        element.text = profile_data.get(field, "")
                
                tree.write(path)

    def append_dialogue(self, user_id: str, user_input: str, 
                       system_response: str, mode: str = "standard") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        dialogue_history = root.find("./Dynamic/DialogueHistory")
        turn = ET.SubElement(dialogue_history, "Turn")
        ET.SubElement(turn, "User").text = user_input
        ET.SubElement(turn, "System").text = system_response
        tree.write(path)

    def get_user_profile(self, user_id: str, mode: str = "standard") -> Dict:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        
        profile = {}
        user_profile = root.find("./Static/UserProfile")
        if user_profile is not None:
            for field in self.schema_config.keys():
                element = user_profile.find(field)
                profile[field] = element.text if element is not None else ""

        # Add other profile elements
        elements = {
            "content_bias": "./Static/ContentBiases/Bias",
            "mental_state": "./Dynamic/PredictedMentalState/State",
            "dialogue_bias": "./Dynamic/PredictedUserDialogueBias/Bias"
        }
        
        for key, xpath in elements.items():
            element = root.find(xpath)
            profile[key] = element.text if element is not None else ""
        
        return profile

    def get_user_profile_content_maxim_evaluation(self, user_id: str, mode: str = "file_maxim_evaluation") -> Dict:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        
        profile = {}
        user_profile = root.find("./Static/UserProfile")
        if user_profile is not None:
            for field in self.schema_config.keys():
                element = user_profile.find(field)
                profile[field] = element.text if element is not None else ""

        # Add other profile elements
        elements = {
            "content_maxim_evaluation": "./Static/ContentEvaluation",
            "mental_state": "./Dynamic/PredictedMentalState/State",
            "llm_dialogue_evaluation": "./Dynamic/DialogueMaximEvaluation"
        }
        
        for key, xpath in elements.items():
            element = root.find(xpath)
            profile[key] = element.text if element is not None else ""
        
        return profile
    
    def update_dynamic_mental_state(self, user_id: str, new_state: str, 
                                   mode: str = "standard") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        mental_state = root.find("./Dynamic/PredictedMentalState")
        mental_state.find("State").text = new_state
        tree.write(path)

    def update_predicted_content_bias(self, user_id: str, bias_value: str, 
                                     mode: str = "standard") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        static = root.find("./Static/ContentBiases")
        static.find("Bias").text = bias_value
        tree.write(path)

    def update_predicted_user_dialogue_bias(self, user_id: str, bias_value: str, 
                                          mode: str = "standard") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        dynamic = root.find("./Dynamic/PredictedUserDialogueBias")
        dynamic.find("Bias").text = bias_value
        tree.write(path)

    def get_dialogue_history(self, user_id: str, mode: str = "standard") -> list:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        return [
            {"user": turn.find("User").text, "system": turn.find("System").text}
            for turn in root.findall("./Dynamic/DialogueHistory/Turn")
        ]

    def reset_dynamic(self, user_id: str, mode: str = "standard") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        dynamic = root.find("./Dynamic")
        
        # Clear existing dynamic content
        for child in list(dynamic):
            dynamic.remove(child)
        
        # Reinitialize dynamic elements
        ET.SubElement(dynamic, "DialogueHistory")
        mental_state = ET.SubElement(dynamic, "PredictedMentalState")
        ET.SubElement(mental_state, "State").text = "Neutral"
        pred_dialogue_bias = ET.SubElement(dynamic, "PredictedUserDialogueBias")
        ET.SubElement(pred_dialogue_bias, "Bias").text = "None"
        
        tree.write(path)
        
    def update_predicted_content_maxim_evaluation(self, user_id: str, maxim_evaluation: dict, 
                                                    mode: str = "file_maxim_evaluation") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        static = root.find("./Static/ContentEvaluation")
        # Create a new element for the maxim evaluation JSON output
        # maxim_elem = ET.Element("MaximEvaluation")
        # maxim_elem.text = json.dumps(maxim_evaluation)
        static.text = json.dumps(maxim_evaluation)
        # static.append(maxim_elem)
        
        tree.write(path)


    def update_predicted_LLM_dialogue_maxim_evaluations(self, user_id: str, maxim_evaluation: dict, 
                                                        mode: str = "file_maxim_evaluation") -> None:
        path = self.get_user_xml_path(user_id, mode)
        tree = ET.parse(path)
        root = tree.getroot()
        dynamic = root.find("./Dynamic/DialogueMaximEvaluation")
        dynamic.text = json.dumps(maxim_evaluation)
        tree.write(path)