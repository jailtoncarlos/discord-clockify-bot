# Discord Clockify Bot

[![Docker Build](https://img.shields.io/docker/automated/discord-clockify-bot.svg?label=Docker%20Build&style=flat-square)](https://hub.docker.com/r/discord-clockify-bot)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

Um bot de Discord que inicia automaticamente o timer do Clockify quando um usuário entra em um canal de voz, e finaliza o timer ao sair.

---

## Estrutura de Diretórios

```plaintext
discord-clockify-bot/
├── bot/                        # Código-fonte principal do bot
│   ├── __init__.py
│   ├── main.py                 # Ponto de entrada do bot
│   ├── clockify_client.py      # Módulo de comunicação com a API do Clockify
│   ├── voice_handler.py        # Lógica de tratamento dos eventos de voz do Discord
│   ├── user_registry.py        # Módulo responsável pelo mapeamento dos usuários
│
├── config/
│   ├── __init__.py
│   ├── settings.py             # Carregamento de variáveis do ambiente (.env)
│   ├── config_loader.py        # Funções utilitárias para acesso às configurações
│   ├── config.json             # Configuração real com chaves (não versionar)
│   └── config.json.sample      # Exemplo de configuração (pode versionar)
│
├── .env                        # Variáveis de ambiente sensíveis (não versionar)
├── .gitignore                  # Ignorar arquivos sensíveis e de build
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação do projeto
└── run.py                      # Atalho de execução (importa e executa bot.main)
```

## Descrição dos Principais Arquivos

- `run.py`: script simples para iniciar o bot.
- `bot/main.py`: contém a configuração do client do Discord e os eventos principais.
- `bot/voice_handler.py`: escuta `on_voice_state_update` e aciona os métodos do `clockify_client`.
- `bot/clockify_client.py`: implementa chamadas HTTP para iniciar e encerrar os timers no Clockify.
- `config/settings.py`: encapsula as variáveis de ambiente com o uso de `dotenv`, carrega `config.json`.

---

## Como Executar o Projeto

### Requisitos

- Docker e Docker Compose instalados
- Token do Bot do Discord
- API Key da conta Clockify
- Arquivo `.env` com as credenciais e configurações
- Mapeamento de usuários no arquivo `config/users_map.json`

---

### Arquivo `.env` (exemplo)

```env
DISCORD_TOKEN=seu_token_do_bot
LOG_LEVEL=INFO
```

> O arquivo `.env` contém variáveis de ambiente sensíveis (como o token do bot).
> 
> - **Não versionar**: adicione `.env` ao `.gitignore`.
> - Use o arquivo `.env.sample` como base para configurar o seu ambiente:
>
> ```bash
> cp .env.sample .env
> ```
>
> Em produção, pode-se definir essas variáveis diretamente no ambiente ou em um arquivo `.env` montado como volume no container.


---

### Arquivo `config/users_map.json`

Exemplo de mapeamento de usuários Discord para usuários do Clockify:

```json
{
  "discord_channels": {
    "DISCORD_CHANNEL_ID_EXEMPLO": {
      "clockify_workspace_id": "WORKSPACE_ID_EXEMPLO",
      "clockify_project_id": "PROJECT_ID_EXEMPLO",
      "discord_server_id": "DISCORD_SERVER_ID_EXEMPLO"
    }
  },
  "discord_users": {
    "DISCORD_USER_ID-DISCORD_CHANNEL_ID_EXEMPLO": {
      "clockify_api_key": "SUA_CLOCKIFY_API_KEY",
      "clockify_user_id": "CLOCKIFY_USER_ID_EXEMPLO",
      "name": "NOME_DO_USUARIO"
    }
  }
}
```


>  O arquivo config/config.json não deve ser versionado. Use config.json.sample como base e adicione config.json ao .gitignore.

#### Como obter os IDs

##### 1. Ative o modo desenvolvedor no Discord:
1. **Abra o Discord** (aplicativo ou navegador)
2. No canto inferior esquerdo, clique no **ícone de engrenagem ⚙️** ao lado do seu nome → isso abre as **Configurações do Usuário**
3. No menu lateral esquerdo, role até a seção **“Avançado”** (Advanced)
4. Ative a opção **“Modo Desenvolvedor” (Developer Mode)**

##### Ver o ID do usuário
1. Acesse as configurações do servidor (Server Settings)
2. Clique em **Membros** (Members)
3. Clique com o botão direito no nome do usuário → **Copiar ID** (Copy ID)

#### ID do usuário no Clockify

1. Use a API:

```http
curl -s -H "X-Api-Key: SUA_API_KEY" https://api.clockify.me/api/v1/workspaces/WORKSPACE_ID/users

```

2. Ou acesse o painel e abra o perfil do membro:
   - [https://app.clockify.me/workspaces/<workspaceId>/team](https://app.clockify.me/workspaces/<workspaceId>/team)
   - Clique no nome → o ID aparece na URL

---

## Execução com Docker Compose (Desenvolvimento)

### Construir a imagem (primeira vez ou após alterações)

```bash
docker-compose build
```

### Subir o bot em modo background

```bash
docker-compose up -d
```

### Ver os logs do bot

```bash
docker-compose logs -f
```

### Parar e remover o container

```bash
docker-compose down
```

> 💡 O `docker-compose.yml` carrega automaticamente o `.env` e monta `config/` como volume somente leitura.  
> O `docker-compose.override.yml` complementa com opções úteis em desenvolvimento (como `tty`, `stdin_open`, logs rotacionados).

---

## Execução em Produção com `docker-compose.prod.yml`

Para ambiente de produção, use o `docker-compose.prod.yml`, que aplica boas práticas adicionais de segurança e estabilidade:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Este modo inclui:

- Container com filesystem somente leitura (`read_only`)
- Logs rotacionados e limitação de tamanho
- Montagem segura de volumes (`:ro`)
- Sem interatividade (sem `tty` e `stdin_open`)
- Rede isolada (`bot-net`)

---

## Execução Local (sem Docker - opcional)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python run.py
```

---

## Publicação Automatizada com GitHub Actions

Este projeto está configurado para publicar automaticamente uma imagem Docker no [Docker Hub](https://hub.docker.com/) sempre que houver:

- Push na branch `main`
- Criação de um release

### Como funciona

1. A imagem é construída via GitHub Actions (`.github/workflows/docker-publish.yml`)
2. A imagem é publicada com as tags:
   - `latest`
   - `sha-<commit>`
   - `<release-tag>` (se aplicável)

### Secrets necessários no GitHub

No repositório → Settings → Secrets → Actions:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN` (usar token de acesso do Docker Hub)
- `IMAGE_NAME` (ex: `jailtoncarlos/discord-clockify-bot`)

> Isso permite deploys consistentes usando `docker-compose.prod.yml` diretamente com a imagem publicada.

---

## 📝 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).


