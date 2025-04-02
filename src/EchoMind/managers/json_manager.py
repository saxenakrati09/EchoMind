import os
import json
from typing import Optional, Dict
from icecream import ic

class JsonManager:
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
        
    def get_user_json_path(self, user_id: str, mode: str = "standard") -> str:
        return os.path.join("generated_data/users", f"{user_id}_{mode}.json")

    def initialize_user_json(self, user_id: str, profile_data: Dict[str, str], 
                           content_bias: str = "None", mode: str = "standard") -> None:
        path = self.get_user_json_path(user_id, mode)
        if not os.path.exists("generated_data/users"):
            os.makedirs("generated_data/users")
        if not os.path.exists(path):
            data = {
                "Static": {
                    "UserProfile": {field: profile_data.get(field, "") for field in self.schema_config},
                    "ContentBiases": {"Bias": content_bias}
                },
                "Dynamic": {
                    "DialogueHistory": [],
                    "PredictedMentalState": {"State": "Neutral"},
                    "PredictedUserDialogueBias": {"Bias": "None"}
                }
            }
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
            
    def initialize_user_json_file(self, user_id: str, profile_data: Dict[str, str], 
                           content_bias: str = "None", mode: str = "file") -> None:
        path = self.get_user_json_path(user_id, mode)
        if not os.path.exists("generated_data/users"):
            os.makedirs("generated_data/users")
        if not os.path.exists(path):
            data = {
                "Static": {
                    "UserProfile": {field: profile_data.get(field, "") for field in self.schema_config},
                    "ContentBiases": {"Bias": content_bias}
                },
                "Dynamic": {
                    "DialogueHistory": [],
                    "PredictedMentalState": {"State": "Neutral"},
                    "PredictedUserDialogueBias": {"Bias": "None"}
                }
            }
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)

    def update_static_profile(self, user_id: str, profile_data: Dict[str, str]) -> None:
        for mode in ["standard", "file"]:
            path = self.get_user_json_path(user_id, mode)
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                user_profile = data["Static"]["UserProfile"]
                for field in self.schema_config:
                    user_profile[field] = profile_data.get(field, "")
                with open(path, 'w') as f:
                    json.dump(data, f, indent=2)

    def append_dialogue(self, user_id: str, user_input: str, 
                       system_response: str, mode: str = "standard") -> None:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        data["Dynamic"]["DialogueHistory"].append({
            "user": user_input,
            "system": system_response
        })
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_user_profile(self, user_id: str, mode: str = "standard") -> Dict:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        profile = {}
        user_profile = data["Static"]["UserProfile"]
        for field in self.schema_config:
            profile[field] = user_profile.get(field, "")
        profile["content_bias"] = data["Static"]["ContentBiases"]["Bias"]
        profile["mental_state"] = data["Dynamic"]["PredictedMentalState"]["State"]
        profile["dialogue_bias"] = data["Dynamic"]["PredictedUserDialogueBias"]["Bias"]
        return profile

    def update_dynamic_mental_state(self, user_id: str, new_state: str, 
                                   mode: str = "standard") -> None:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        data["Dynamic"]["PredictedMentalState"]["State"] = new_state
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def update_predicted_content_bias(self, user_id: str, bias_value: str, 
                                    mode: str = "standard") -> None:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        data["Static"]["ContentBiases"]["Bias"] = bias_value
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def update_predicted_user_dialogue_bias(self, user_id: str, bias_value: str, 
                                         mode: str = "standard") -> None:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        data["Dynamic"]["PredictedUserDialogueBias"]["Bias"] = bias_value
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def get_dialogue_history(self, user_id: str, mode: str = "standard") -> list:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        return data["Dynamic"]["DialogueHistory"]

    def reset_dynamic(self, user_id: str, mode: str = "standard") -> None:
        path = self.get_user_json_path(user_id, mode)
        with open(path, 'r') as f:
            data = json.load(f)
        data["Dynamic"] = {
            "DialogueHistory": [],
            "PredictedMentalState": {"State": "Neutral"},
            "PredictedUserDialogueBias": {"Bias": "None"}
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)