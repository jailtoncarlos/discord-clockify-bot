import json
import logging
from typing import Optional, Union

import requests
from datetime import datetime, timezone
from discord import Member, User
from discord.channel import VocalGuildChannel, TextChannel, DMChannel

from web.crud import CRUDManager
from db.database import engine
from web.models import UserProjectChannelBinding, ClockifyProject, ClockifyUser

logger = logging.getLogger(__name__)

crud = CRUDManager(engine)

# Mapeia membros do Discord → informações do timer ativo
active_entries: dict[str, dict] = {}  # key = member.id (str)


def has_active_timer(member: Member) -> bool:
    return member.id in active_entries


def build_headers(api_key: str):
    logger.debug("Construindo headers para a requisição Clockify")
    logger.debug(f"API Key utilizada: {api_key[:5]}... (ocultada)")
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }


def get_active_time_entry(discord_user_id: str,
                          server_id: Optional[str] = None,
                          workspace_id: Optional[str] = None,
                          clockify_user_id: Optional[str] = None,
                          api_key: Optional[str] = None) -> Optional[dict]:
    """
    Consulta a API do Clockify para verificar se há um timer ativo para o usuário informado.

    :param clockify_user_id: ID do usuário no Clockify.
    :param workspace_id: ID do workspace no Clockify.
    :param api_key: Chave da API do Clockify (normalmente associada ao usuário).
    :return: Dicionário com o time entry ativo, se houver. Caso contrário, retorna None.
    """
    def get_active_time(clockify_user_id: str, api_key: str, workspace_id: str):
        url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/user/{clockify_user_id}/time-entries?in-progress=true"
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }
        try:
            logger.debug(f"Verificando timer ativo para o usuário {clockify_user_id} no workspace {workspace_id}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            logger.debug(f"Dados retornados da API: {json.dumps(data, indent=2)}")
            breakpoint()
            if data:
                logger.debug(f"Timer ativo encontrado: {data[0]}")
                return data[0]
            logger.debug("Nenhum time ativo encontrado.")
            return None
        except requests.RequestException as e:
            # Pode-se usar logging ao invés de print
            print(f"[Clockify API] Erro ao verificar timer ativo: {e}")
            return None

    entry = active_entries.get(clockify_user_id)
    if entry:
        logger.debug(f"Cache timer ativo encontrado para o usuário {clockify_user_id}: {entry}")
        return entry

    entry = None
    project_id = None
    entry_id = None
    if clockify_user_id and workspace_id and api_key:
        entry = get_active_time(clockify_user_id, api_key, workspace_id)
    else:
        if server_id:
            bindings = crud.get_bindings_by_user_and_server(discord_user_id, server_id)
            for binding in bindings:
                projeto = binding.clockify_user.project
                project_id = projeto.id

                clockify_user_id = binding.clockify_user.id
                api_key = binding.clockify_user.api_key
                workspace_id = projeto.workspace.id

                entry = get_active_time(clockify_user_id, api_key, workspace_id)
                if entry:
                    break

    if entry:
        active_entries[discord_user_id] = {
            "entry_id": entry_id,
            "clockify_user_id": clockify_user_id,
            "project_config": {
                "clockify_workspace_id": workspace_id,
                "clockify_project_id": project_id,
                "clockify_api_key": api_key
            }
        }
        return active_entries[discord_user_id]
    return None


def start_timer(member: Member, channel: VocalGuildChannel, user_link: UserProjectChannelBinding):
    if member is None or channel is None or user_link is None:
        raise ValueError("Membro, canal ou link de usuário não podem ser None.")

    channel_name = channel.name
    channel_id = channel.id

    clockify_user = user_link.clockify_user
    discord_channel = user_link.discord_channel
    project = discord_channel.project
    workspace = project.workspace

    logger.debug(f"Iniciando timer para {member.display_name} ({member.id}) no canal {channel_name} ({channel_id}) do Discord")

    url = f"https://api.clockify.me/api/v1/workspaces/{workspace.id}/user/{clockify_user.id}/time-entries"
    logger.debug(f"URL da requisição: {url}")

    data = {
        "start": datetime.now(timezone.utc).isoformat(),
        "description": f"Tempo iniciado por {member.display_name} no canal {channel_name} do Discord",
        "projectId": project.id
    }

    logger.debug("Payload enviado:")
    logger.debug(json.dumps(data, indent=2))

    response = requests.post(url, headers=build_headers(clockify_user.api_key), json=data)

    if response.status_code == 201:
        entry_id = response.json()["id"]
        active_entries[str({member.id})] = {
            "entry_id": entry_id,
            "clockify_user_id": clockify_user.id,
            "project_config": {
                "clockify_workspace_id": workspace.id,
                "clockify_project_id": project.id,
                "clockify_api_key": clockify_user.api_key
            }
        }
        logger.info(f"Timer iniciado com sucesso para {member.display_name} ({member.id}) no canal {channel_name} ({channel_id}) — Entry ID: {entry_id}")
    else:
        logger.error(f"Erro ao iniciar timer: {response.status_code} - {response.text}")


def stop_timer(member: Member):
    entry = get_active_time_entry(str({member.id}), str(member.guild.id))
    if not entry:
        logger.warning(f"Nenhum timer ativo para {member.display_name} ({member.id}).")
        return

    url = f"https://api.clockify.me/api/v1/workspaces/{entry['project_config']['clockify_workspace_id']}/user/{entry['clockify_user_id']}/time-entries"
    now = datetime.now(timezone.utc).isoformat()
    data = {"end": now}

    logger.debug(f"Encerrando timer para {member.display_name} ({member.id}).")
    logger.debug(f"URL da requisição: {url}")
    logger.debug(f"Payload enviado: {json.dumps(data, indent=2)}")

    response = requests.patch(url, headers=build_headers(entry['project_config']['clockify_api_key']), json=data)

    if response.status_code == 200:
        logger.info(f"Timer encerrado com sucesso para {member.display_name} ({member.id}).")
        active_entries.pop(str({member.id}), None)
    else:
        logger.error(f"Erro ao parar timer: {response.status_code} - {response.text}")


def update_description(member: Union[User, Member], description: str) -> tuple[bool, str]:
    entry = get_active_time_entry(str(member.id), str(member.guild.id))

    if not entry:
        logger.warning(f"Usuário {member.display_name} ({member.id}) não possui timer ativo.")
        return False, "Nenhum timer ativo para atualizar."

    api_key = entry["project_config"]["clockify_api_key"]
    workspace_id = entry["project_config"]["clockify_workspace_id"]
    entry_id = entry["entry_id"]

    url = f"https://api.clockify.me/api/v1/workspaces/{workspace_id}/time-entries/{entry_id}"

    logger.debug(f"Atualizando descrição do timer para {member.display_name} ({member.id}).")
    logger.debug(f"URL da requisição: {url}")

    get_resp = requests.get(url, headers=build_headers(api_key))
    if get_resp.status_code != 200:
        logger.error(f"Erro ao obter entrada de tempo: {get_resp.status_code} - {get_resp.text}")
        return False, f"Erro ao buscar entrada atual: {get_resp.status_code} - {get_resp.text}"

    entry_data = get_resp.json()
    start_time = entry_data.get("timeInterval", {}).get("start")
    if not start_time:
        logger.error(f"Entrada de tempo sem campo 'start': {entry_data}")
        return False, "Erro: entrada de tempo sem campo 'start'."

    payload = {
        "start": start_time,
        "description": description
    }

    logger.debug("Payload enviado para atualização:")
    logger.debug(json.dumps(payload, indent=2))

    put_resp = requests.put(url, headers=build_headers(api_key), json=payload)

    if put_resp.status_code == 200:
        logger.info(f"Descrição do time ativo atualizada com sucesso para {member.display_name} ({member.id})")
        return True, "Descrição do time ativo atualizada com sucesso!"
    else:
        logger.error(f"Erro ao atualizar descrição do time ativo: {put_resp.status_code} - {put_resp.text}")
        return False, f"Erro: {put_resp.status_code} - {put_resp.text}"


def list_tasks(discord_user_id: str, project: ClockifyProject) -> tuple[bool, str]:
    clockify_user = crud.get_clockify_user_by_discord_and_project(discord_user_id, project.id)
    workspace = project.workspace

    if not workspace:
        logger.error("O projeto não possui referência ao workspace.")
        return False, "Workspace não está carregado."

    url = f"https://api.clockify.me/api/v1/workspaces/{workspace.id}/projects/{project.id}/tasks?is-active=true"
    logger.debug(f"Buscando tarefas ativas no projeto {project.name} ({project.id}), workspace {workspace.name} ({workspace.id})...")
    logger.debug(f"URL: {url}")

    response = requests.get(url, headers=build_headers(clockify_user.api_key))

    if response.status_code != 200:
        logger.error(f"Erro ao buscar tarefas: {response.status_code} - {response.text}")
        return False, f"Erro ao buscar tarefas: {response.status_code} - {response.text}"

    tarefas = response.json()
    if not tarefas:
        logger.info(f"Nenhuma tarefa ativa encontrada para o projeto {project.id}.")
        return True, "Nenhuma tarefa ativa encontrada."

    mensagem = "**Tarefas disponíveis:**\n"
    for t in tarefas:
        mensagem += f"• {t['name']} (ID: `{t['id']}`)\n"
    return True, mensagem


def associate_task(member: Union[User, Member], task_id: str) -> tuple[bool, str]:
    entry = get_active_time_entry(str(member.id), str(member.guild.id))

    if not entry:
        logger.warning(f"Nenhum timer ativo para {member.display_name} ({member.id}).")
        return False, "Nenhum timer ativo para associar tarefa."

    url = f"https://api.clockify.me/api/v1/workspaces/{entry['project_config']['clockify_workspace_id']}/time-entries/{entry['entry_id']}"
    payload = {"taskId": task_id}

    logger.debug(f"Associando tarefa {task_id} ao timer ativo de {member.display_name} ({member.id}).")
    logger.debug(f"URL: {url}")
    logger.debug(f"Payload enviado: {json.dumps(payload, indent=2)}")

    response = requests.put(url, headers=build_headers(entry['project_config']['clockify_api_key']), json=payload)

    if response.status_code == 200:
        logger.info(f"Tarefa {task_id} associada ao timer de {member.display_name} ({member.id}).")
        return True, "Tarefa associada com sucesso ao timer!"
    else:
        logger.error(f"Erro ao associar tarefa: {response.status_code} - {response.text}")
        return False, f"Erro: {response.status_code} - {response.text}"
