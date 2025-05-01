import json
import os

USERS_MAP_PATH = os.path.join(os.path.dirname(__file__), "../config/users_map.json")

def load_user_map():
    with open(USERS_MAP_PATH, encoding='utf-8') as f:
        return json.load(f)

def get_clockify_user_id(discord_user_id: int) -> str | None:
    user_map = load_user_map()
    user_data = user_map.get(str(discord_user_id))
    return user_data.get("clockify_user_id") if user_data else None
