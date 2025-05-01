import json

import requests
from datetime import datetime, timezone
from config import settings

HEADERS = {
    "X-Api-Key": settings.CLOCKIFY_API_KEY,
    "Content-Type": "application/json"
}

active_entries = {}  # user_id → entry_id


def start_timer(user_id: int, clockify_user_id: str):
    url = f"https://api.clockify.me/api/v1/workspaces/{settings.CLOCKIFY_WORKSPACE_ID}/user/{clockify_user_id}/time-entries"

    data = {
        "start": datetime.now(timezone.utc).isoformat(),
        "description": "Tempo iniciado via Discord"
    }

    if settings.CLOCKIFY_PROJECT_ID:
        data["projectId"] = settings.CLOCKIFY_PROJECT_ID

    print(f"[DEBUG] Iniciando timer para {user_id} (Clockify ID: {clockify_user_id})")
    print(f"[DEBUG] Payload enviado: {json.dumps(data, indent=2)}")

    response = requests.post(url, headers=HEADERS, json=data)

    if response.status_code == 201:
        entry_id = response.json()["id"]
        active_entries[user_id] = entry_id
        print(f"[+] Timer iniciado para {user_id} (entry_id: {entry_id})")
    else:
        print(f"[ERRO] Falha ao iniciar timer para {user_id}")
        print(f"      Status: {response.status_code}")
        print(f"      Resposta: {response.text}")


def stop_timer(user_id: int, clockify_user_id: str):
    url = f"https://api.clockify.me/api/v1/workspaces/{settings.CLOCKIFY_WORKSPACE_ID}/user/{clockify_user_id}/time-entries"
    now = datetime.now(timezone.utc).isoformat()

    data = {
        "end": now
    }

    print(f"[DEBUG] Encerrando timer atual para usuário {user_id} (Clockify ID: {clockify_user_id})")
    print(f"[DEBUG] Payload enviado: {json.dumps(data, indent=2)}")

    response = requests.patch(url, headers=HEADERS, json=data)

    if response.status_code == 200:
        print(f"[-] Timer finalizado com sucesso para {user_id}")
        active_entries.pop(user_id, None)
    else:
        print(f"[!] Erro ao parar timer: {response.status_code} - {response.text}")
