import json
from pathlib import Path
from sqlmodel import Session, create_engine

from db.database import engine, create_db_and_tables
from web.crud import CRUDManager
from web.models import (
    ClockifyWorkspace,
    ClockifyProject,
    ClockifyUser,
    DiscordServer,
    DiscordChannel,
    DiscordUser,
    UserProjectChannelBinding,
)

# Cria as tabelas se ainda não existirem
create_db_and_tables()

# Caminho do arquivo JSON
json_path = Path("config/config.json")  # ou ajuste para o caminho real

# Carrega os dados
with json_path.open("r", encoding="utf-8") as f:
    data = json.load(f)


with Session(engine) as session:
    crud = CRUDManager(session)

    # ----- Criação dos canais e dependências -----
    for channel_id, info in data["discord_channels"].items():
        workspace_id = info["clockify_workspace_id"]
        project_id = info["clockify_project_id"]
        server_id = info["discord_server_id"]

        # Workspace
        if not crud.get_by_id(ClockifyWorkspace, workspace_id):
            crud.create(ClockifyWorkspace(id=workspace_id, name="iService"))

        # Projeto
        if not crud.get_by_id(ClockifyProject, project_id):
            crud.create(ClockifyProject(id=project_id, name="iService", workspace_id=workspace_id))

        # Servidor
        if not crud.get_by_id(DiscordServer, server_id):
            crud.create(DiscordServer(id=server_id, name="iService"))

        # Canal
        if not crud.get_by_id(DiscordChannel, channel_id):
            crud.create(
                DiscordChannel(
                    id=channel_id,
                    name="iService",
                    server_id=server_id,
                    project_id=project_id,
                )
            )

    # ----- Criação dos usuários -----
    for compound_id, user_info in data["discord_users"].items():
        discord_user_id, channel_id = compound_id.split("-")
        project_id = data["discord_channels"][channel_id]["clockify_project_id"]
        server_id = data["discord_channels"][channel_id]["discord_server_id"]
        clockify_user_id = user_info["clockify_user_id"]

        # ClockifyUser
        if not crud.get_by_id(ClockifyUser, clockify_user_id):
            crud.create(
                ClockifyUser(
                    id=clockify_user_id,
                    name=user_info["name"],
                    api_key=user_info["clockify_api_key"],
                    project_id=project_id,
                )
            )

        # DiscordUser
        if not crud.get_by_id(DiscordUser, discord_user_id):
            crud.create(DiscordUser(id=discord_user_id, server_id=server_id))

        # UserAccountLink
        link_id = f"{discord_user_id}-{channel_id}"
        if not crud.get_by_id(UserProjectChannelBinding, link_id):
            crud.create(
                UserProjectChannelBinding(
                    id=f"{discord_user_id}-{channel_id}",
                    discord_user_id=discord_user_id,
                    clockify_user_id=clockify_user_id,
                    discord_channel_id=channel_id,
                )
            )
