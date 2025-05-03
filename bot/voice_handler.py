from discord import Member, VoiceState, Forbidden
import logging
from bot import clockify_client
from web.commands.migrar_config_json import crud
from web.models import DiscordChannel, UserProjectChannelBinding

logger = logging.getLogger(__name__)


async def handle_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    channel = after.channel if after.channel else before.channel
    if not channel:
        return

    channel_id = str(channel.id)
    user_id = str(member.id)

    # Verifica se o canal está cadastrado
    canal = crud.get_by_id(DiscordChannel, channel_id)
    if not canal:
        logger.warning(f"Canal {channel_id} não associado a nenhum projeto Clockify.")
        return


    # Verifica se o usuário está vinculado ao canal
    account_link_id = f"{user_id}-{channel_id}"
    user_link = crud.get_by_id(UserProjectChannelBinding, account_link_id)

    if not user_link:
        logger.warning(f"Usuário Discord {user_id} não está mapeado no projeto do canal {channel_id}.")
        return

    if before.channel is None and after.channel is not None:
        logger.info(f"{member.display_name} entrou em {after.channel.name}")
        clockify_client.start_timer(member, channel, user_link)

        if not crud.has_been_notified(str(member.id)):

            discord_user = user_link.discord_user
            if not discord_user.name:
                logger.debug(f"Atualizando nome do DiscordUser {user_id} para '{member.display_name}'")
                discord_user.name = member.display_name
                crud.session.add(discord_user)
                crud.session.commit()

            try:
                logger.debug(f"Enviando DM para {member.display_name} ({member.id})")
                await member.send(
                    f"Seu timer foi iniciado com sucesso!\n\n"
                    f"Você pode utilizar os seguintes comandos:\n"
                    f"• `/descricao [tarefa que está realizando]`\n"
                    f"   → Atualiza a descrição do timer ativo.\n\n"
                    f"• `/listar_tarefas`\n"
                    f"   → Lista as tarefas disponíveis no projeto associado ao canal.\n\n"
                    f"• `/usar_tarefa [ID da tarefa]`\n"
                    f"   → Associa uma das tarefas listadas ao timer em execução.\n\n"
                    f"Exemplo:\n"
                    f"`/descricao Revisando documentação do módulo X`\n"
                    f"`/usar_tarefa 64f20512ec78b212d730ce2a`\n\n"
                    f"Você pode usar os comandos por aqui (mensagem direta) ou em qualquer canal de texto do servidor."
                )
                crud.mark_as_notified(str(member.id))
            except Forbidden:
                logger.error(f"[!] Não foi possível enviar DM para {member.display_name}.")

    elif before.channel is not None and after.channel is None:
        logger.info(f"{member.display_name} saiu de {before.channel.name}")
        clockify_client.stop_timer(member)
