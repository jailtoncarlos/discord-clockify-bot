from discord import Member, VoiceState
import logging
from bot import clockify_client
from config.config_loader import get_project_by_channel_entry, get_user_entry

logger = logging.getLogger(__name__)


async def handle_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    channel = after.channel if after.channel else before.channel
    if not channel:
        return

    channel_id = channel.id
    channel_config = get_project_by_channel_entry(channel_id)

    if not channel_config:
        logger.warning(f"Canal {channel_id} não associado a nenhum projeto Clockify.")
        return

    user_entry = get_user_entry(member.id, channel_id)
    if not user_entry:
        logger.warning(f"Usuário Discord {member.id} não está mapeado no projeto do canal {channel_id}.")
        return

    if before.channel is None and after.channel is not None:
        logger.info(f"{member.display_name} entrou em {after.channel.name}")
        clockify_client.start_timer(member, channel, user_entry, channel_config)

    elif before.channel is not None and after.channel is None:
        logger.info(f"{member.display_name} saiu de {before.channel.name}")
        clockify_client.stop_timer(member, user_entry, channel_config)
