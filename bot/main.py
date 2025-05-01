import discord
from config import settings
import logging
from bot.voice_handler import handle_voice_state_update

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)

def run_bot():
    client.run(settings.DISCORD_TOKEN)


@client.event
async def on_ready():
    logger.info(f"[BOT ATIVO] Conectado como {client.user}")


@client.event
async def on_voice_state_update(member, before, after):
    await handle_voice_state_update(member, before, after)
