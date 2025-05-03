import os
from pathlib import Path
from sqlmodel import SQLModel, create_engine

from config.settings import SQLALCHEMY_ECHO
# Importa explicitamente os modelos antes de criar o banco
from web.models import (
    ClockifyWorkspace,
    ClockifyProject,
    ClockifyUser,
    DiscordServer,
    DiscordChannel,
    DiscordUser,
    UserNotification,
    UserProjectChannelBinding,
)

# Caminho absoluto do banco de dados
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Engine global
engine = create_engine(DATABASE_URL, echo=SQLALCHEMY_ECHO)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
