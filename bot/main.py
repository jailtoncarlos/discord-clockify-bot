import logging
import asyncio
from discord import Intents
from discord.ext import commands

from bot.tasks.presence_verifier import PresenceVerifier
from config import settings
from bot.voice_handler import handle_voice_state_update
from db.database import create_db_and_tables

logger = logging.getLogger(__name__)

intents = Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Cria as tabelas se ainda não existirem
create_db_and_tables()

def run_bot():
    async def start():
        await bot.load_extension("bot.commands")
        await bot.start(settings.DISCORD_TOKEN)

    asyncio.run(start())


@bot.event
async def on_ready():
    logger.info(f"[BOT ATIVO] Conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        logger.info(f"[✓] Slash commands sincronizados: {[cmd.name for cmd in synced]}")
    except Exception as e:
        logger.error(f"[X] Erro ao sincronizar comandos: {e}")

    PresenceVerifier(
        bot,
        interval_minutes=settings.PRESENCE_DM_INTERVAL_MINUTES,
        timeout_seconds=settings.PRESENCE_RESPONSE_TIMEOUT_SECONDS
    )



@bot.event
async def on_voice_state_update(member, before, after):
    await handle_voice_state_update(member, before, after)
