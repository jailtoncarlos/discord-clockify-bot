import json
import logging
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do nível de log via variável de ambiente, se desejar
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

# Remove qualquer handler pré-existente antes de configurar
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configuração global de logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

CONFIG_PATH = Path(__file__).parent / "config.json"

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

DISCORD_CHANNELS = CONFIG["discord_channels"]
DISCORD_USERS = CONFIG["discord_users"]

