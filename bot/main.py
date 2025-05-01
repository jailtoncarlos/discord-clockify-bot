import discord
from bot.voice_handler import handle_voice_state_update

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)

def run_bot():
    from config import settings
    client.run(settings.DISCORD_TOKEN)

@client.event
async def on_ready():
    print(f"[BOT ATIVO] Conectado como {client.user}")

@client.event
async def on_voice_state_update(member, before, after):
    await handle_voice_state_update(member, before, after)
