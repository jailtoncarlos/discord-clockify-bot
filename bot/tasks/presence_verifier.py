import asyncio
import logging
from discord import Member, VoiceChannel
from discord.ext import tasks

from config import settings
from db.database import engine
from sqlmodel import Session
from web.crud import CRUDManager
from web.models import UserProjectChannelBinding
from bot.clockify_client import has_active_timer, start_timer, stop_timer

logger = logging.getLogger(__name__)


class PresenceVerifier:
    def __init__(self, bot, interval_minutes: int, timeout_seconds: int):
        self.bot = bot
        self.interval_minutes = interval_minutes
        self.timeout_seconds = timeout_seconds
        self.session = Session(engine)
        self.crud = CRUDManager(self.session)

        # Ajusta o intervalo dinamicamente e inicia a tarefa
        self.verificar_presenca.change_interval(minutes=self.interval_minutes)
        self.verificar_presenca.start()

    @tasks.loop(minutes=settings.PRESENCE_DM_INTERVAL_MINUTES)  # Substituído dinamicamente por change_interval
    async def verificar_presenca(self):
        await asyncio.sleep(10)  # Delay inicial para evitar conflitos com eventos de inicialização

        bindings = self.crud.get_all_bindings_with_channel()
        for binding in bindings:
            try:
                discord_user = await self.bot.fetch_user(int(binding.discord_user_id))
                if not discord_user:
                    logger.warning(f"Usuário Discord {binding.discord_user_id} não encontrado.")
                    continue

                channel = binding.discord_channel
                if not channel:
                    logger.warning(f"Vínculo {binding.id} não possui canal de voz associado.")
                    continue

                await self.enviar_verificacao(discord_user, binding, channel)

            except Exception:
                logger.exception(f"Erro ao processar verificação de presença para {binding.discord_user_id}")

    async def enviar_verificacao(self, discord_user: Member, binding: UserProjectChannelBinding, channel: VoiceChannel):
        try:
            mensagem = await discord_user.send("Você ainda está aí? Responda 'sim' para confirmar sua presença.")

            def check(m):
                return (
                    m.author.id == discord_user.id and
                    m.channel.id == mensagem.channel.id and
                    m.content.lower().strip() == "sim"
                )

            try:
                await self.bot.wait_for("message", timeout=self.timeout_seconds, check=check)

                if not has_active_timer(discord_user):
                    start_timer(discord_user, channel, binding)
                    await discord_user.send("Timer iniciado no Clockify.")
                else:
                    await discord_user.send("Presença confirmada. O timer já está ativo.")

            except asyncio.TimeoutError:
                if has_active_timer(discord_user):
                    stop_timer(discord_user)
                    await discord_user.send("Você não respondeu. O timer foi encerrado no Clockify.")
                    logger.info(f"[Ausência] Timer encerrado para {discord_user.display_name} ({discord_user.id})")

        except Exception:
            logger.exception(f"Erro ao interagir via DM com {discord_user.display_name} ({discord_user.id})")
