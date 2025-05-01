import json
import logging
from datetime import datetime, timezone
from discord import Member, VoiceState
import requests
from discord.channel import VocalGuildChannel

logger = logging.getLogger(__name__)

# user_id (Discord) → entry_id
active_entries = {}


def build_headers(api_key: str):
    logger.debug("Construindo headers para a requisição")
    logger.debug(f"API Key: {api_key}")
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }


def start_timer(member: Member, channel: VocalGuildChannel, user_entry: dict, channel_entry: dict):
    clockify_user_id = user_entry["clockify_user_id"]
    clockify_api_key = user_entry["clockify_api_key"]
    workspace_id = channel_entry["clockify_workspace_id"]
    project_id = channel_entry.get("clockify_project_id")

    url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{clockify_user_id}/time-entries"
    logger.debug(f"URL: {url}")

    data = {
        "start": datetime.now(timezone.utc).isoformat(),
        "description": f"Tempo iniciado por {member.display_name} no canal {channel.name} do Discord",
    }

    if project_id:
        data["projectId"] = project_id

    logger.debug(f"Iniciando timer para Usuario Discord: {member.display_name} ({member.id}), Usuário Clockify ID: {clockify_user_id}")
    logger.debug(f"Payload enviado: {json.dumps(data, indent=2)}")

    response = requests.post(url, headers=build_headers(clockify_api_key), json=data)

    if response.status_code == 201:
        entry_id = response.json()["id"]
        active_entries[member.id] = {
            "entry_id": entry_id,
            "clockify_user_id": clockify_user_id,
            "project_config": channel_entry
        }
        logger.info(f"Timer iniciado para Usuario Discord: {member.display_name} ({member.id}), Entry ID: {entry_id}")
    else:
        logger.error(f"Falha ao iniciar timer para Usuario Discord: {member.display_name} ({member.id})")
        logger.error(f"Status: {response.status_code}")
        logger.error(f"Resposta: {response.text}")


def stop_timer(member: Member, user_entry: dict, channel_config: dict):
    clockify_user_id = user_entry["clockify_user_id"]
    clockify_api_key = user_entry["clockify_api_key"]
    workspace_id = channel_config["clockify_workspace_id"]

    url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{clockify_user_id}/time-entries"
    logger.debug(f"URL: {url}")
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "end": now
    }

    logger.debug(f"Encerrando timer atual para Usuario Discord: {member.display_name} ({member.id}), Usuário Clockify: {clockify_user_id}")
    logger.debug(f"Payload enviado: {json.dumps(data, indent=2)}")

    response = requests.patch(url, headers=build_headers(clockify_api_key), json=data)

    if response.status_code == 200:
        logger.info(f"Timer finalizado com sucesso para Usuario Discord: {member.display_name} ({member.id})")
        active_entries.pop(member.id, None)
    else:
        logger.error(f"Erro ao parar timer: {response.status_code} - {response.text}")
