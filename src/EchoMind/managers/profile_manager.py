import os
import json
from typing import Optional, Dict, List
from icecream import ic
from collections import defaultdict

if not os.path.exists("generated_data"):
    os.makedirs("generated_data")
    
GLOBAL_PROFILES_FILE = "generated_data/global_profiles.json"

class ProfileManager:
    def __init__(self, schema_config_path: Optional[str] = None):
        self.schema_config_path = schema_config_path
        self.schema_config = self._load_schema_config()
        
    def _load_schema_config(self) -> Dict[str, List[str]]:
        try:
            with open(self.schema_config_path, "r") as f:
                config = json.load(f)
            return config.get("schema", {})
        except Exception as e:
            print(f"Error loading schema config: {e}")
            return {}
        
    def load_global_profiles(self) -> List[Dict]:
        if not os.path.exists(GLOBAL_PROFILES_FILE):
            return []
        with open(GLOBAL_PROFILES_FILE, "r") as f:
            return json.load(f)

    def save_global_profiles(self, profiles: List[Dict]) -> None:
        with open(GLOBAL_PROFILES_FILE, "w") as f:
            json.dump(profiles, f, indent=2)

    def update_global_profiles(self, user_profile: Dict) -> None:
        """
        Append the current user profile to the global profiles.
        Filters profile to only include schema-defined fields
        """
        filtered_profile = {
            field: user_profile.get(field, "")
            for field in self.schema_config.keys()
        }
        profiles = self.load_global_profiles()
        profiles.append(filtered_profile)
        self.save_global_profiles(profiles)

    def predict_default_profile(self) -> Dict:
        """
        Predict default profile based on aggregated data and schema configuration.
        For each schema field, uses most common value from historical profiles.
        """
        profiles = self.load_global_profiles()
        default_profile = {}
        
        for field, options in self.schema_config.items():
            if not profiles:
                # Use first option as default if no history exists
                default_profile[field] = options[0] if options else ""
                continue
                
            # Count occurrences of each option
            value_counts = defaultdict(int)
            for profile in profiles:
                value = profile.get(field, "")
                if value in options:
                    value_counts[value] += 1
                    
            if value_counts:
                # Get value with highest count, break ties with first occurrence
                max_count = max(value_counts.values())
                candidates = [k for k, v in value_counts.items() if v == max_count]
                default_profile[field] = candidates[0]
            else:
                # Fallback to first option if no valid values found
                default_profile[field] = options[0] if options else ""
                
        return default_profile