from EchoMind.managers.xml_manager import update_static_profile
from EchoMind.managers.profile_manager import update_global_profiles

def set_profile_callback(expertise, time_available, username):
    if not username:
        return "Error: No user logged in."
    update_static_profile(username, expertise, time_available)
    update_global_profiles({"expertise": expertise, "time_available": time_available})
    return f"Profile updated for {username}: Expertise = {expertise}, Time Available = {time_available}"