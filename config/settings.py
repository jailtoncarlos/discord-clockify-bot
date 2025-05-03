import json
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")


PRESENCE_DM_INTERVAL_MINUTES = int(os.getenv("PRESENCE_DM_INTERVAL_MINUTES", 30))
PRESENCE_RESPONSE_TIMEOUT_SECONDS = int(os.getenv("PRESENCE_RESPONSE_TIMEOUT_SECONDS", 60))


# Configuração do nível de log via variável de ambiente, se desejar
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "false").lower() in ("1", "true", "yes")

# Desativa logs específicos com base em variáveis do .env
LOG_DISCORD = os.getenv("LOG_DISCORD", "false").lower() == "true"


# Remove qualquer handler pré-existente antes de configurar
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configuração global de logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)

if not LOG_DISCORD:
    # Configura logger do Discord.py
    for discord_namespace in ["discord", "discord.gateway", "discord.client", "discord.ext.commands"]:
        logger_ = logging.getLogger(discord_namespace)
        logger_.propagate = False
        logger_.setLevel(logging.DEBUG if LOG_DISCORD else logging.WARNING)

