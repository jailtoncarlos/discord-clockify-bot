from discord import Member, VoiceState
from bot import user_registry, clockify_client

async def handle_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if before.channel is None and after.channel is not None:
        print(f"{member.display_name} entrou em {after.channel.name}")
        clockify_user_id = user_registry.get_clockify_user_id(member.id)
        if clockify_user_id:
            clockify_client.start_timer(member.id, clockify_user_id)
    elif before.channel is not None and after.channel is None:
        print(f"{member.display_name} saiu de {before.channel.name}")
        clockify_client.stop_timer(member.id)
