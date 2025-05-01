from typing import Optional

from config.settings import DISCORD_CHANNELS, DISCORD_USERS


def get_project_by_channel_entry(channel_id: int) -> Optional[dict[str, str]]:
    return DISCORD_CHANNELS.get(str(channel_id))  # retorna o dict do projeto


def get_user_entry(discord_user_id: int, discord_channel_id: str) -> Optional[dict[str, str]]:
    key = f"{discord_user_id}-{discord_channel_id}"
    return DISCORD_USERS.get(key)

