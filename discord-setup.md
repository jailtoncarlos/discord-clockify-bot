# Discord Setup - ClockifyBot

Este documento orienta a configuração completa da aplicação ClockifyBot no Discord Developer Portal, incluindo permissões, intents e URL de convite.

---

## 1. Criar a aplicação no Discord

1. Acesse: [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. Clique em **"New Application"** e dê o nome: `ClockifyBot`
3. Clique no botão "Create". Será aberta a janela "General Information"
4. Opcionalmente, faça upload do ícone do bot (pode ser o mesmo do repositório)
5. Opcionalmente, defina um ícone e preencha:
   - **Description:**
     ```
     ClockifyBot helps development teams automatically track working time in Clockify based on Discord voice channel activity. Time tracking starts when a user joins a voice channel and stops when they leave — simple, smart, and automatic.
     ```
   - **Tags:** `productivity`, `development-tools`, `time-tracking`, `clockify`, `voice-automation`

---

## 2. Criar e configurar o bot

1. No menu lateral, clique em **"Bot"**
2. Clique no botão "Reset Token" para gerar um novo token
   - **Atenção:** O token é sensível e deve ser mantido em segredo. Não compartilhe com ninguém.
   - **Importante:** Se você já tiver um bot, não é necessário criar outro. Você pode usar o mesmo bot para diferentes servidores.
3. Em seguida:
   - Copie o **Token** e salve no seu `.env`:
     ```env
     DISCORD_TOKEN=seu_token_aqui
     ```
   - Ative:
     - [x] **Public Bot** (para poder adicionar em servidores)

4. Em **Privileged Gateway Intents**, ative:
   - [x] **Server Members Intent** ✅ **Obrigatório para mapear o usuário com o Clockify**
   - [ ] **Presence Intent** (opcional)
   - [ ] **Message Content Intent** (não necessário para este bot)
5. Clique no botão "Save Changes" para salvar as alterações

> ❌ Não é necessário ativar nenhuma "Voice State Intent" — ela já está disponível por padrão.

---

## 3. Gerar URL de convite 
### 1. No menu lateral, clique em **"OAuth2"**
Acesse a área **OAuth2 → URL Generator**
  
### 2. Em **Scopes**, marque: `bot`
*(Apenas esta opção por enquanto. Outras são usadas para OAuth2 tradicional, não necessário aqui.)*

### 3. Após marcar `bot`, role para baixo até aparecer a seção **Bot Permissions**

Agora, marque as permissões que o ClockifyBot precisa para funcionar:

| Categoria        | Permissão           |
|------------------|---------------------|
| ✅ General        | View Channels       |
| ✅ Voice          | Connect             |
| ✅ Text           | Send Messages       |
| ✅ Text           | Read Message History |

Essas são as permissões mínimas e suficientes para que o bot:

- Veja os canais de voz
- Detecte quem entrou/saiu
- Envie mensagens (caso deseje logar eventos)

### 4. Role até o final e copie a **Generated URL**

- O campo `GENERATED URL` será preenchido automaticamente
- Clique em **Copy**
- Abra essa URL em seu navegador para **autorizar o bot em um servidor**

**Exemplo de URL gerada**

Será parecida com:

```
https://discord.com/oauth2/authorize?client_id=1367513418982096987&permissions=1117184&integration_type=0&scope=bot
```

> ⚠️ A URL é válida **somente se o bot ainda existir**, e o `client_id` for o da sua aplicação.


### 5. Acesse a URL em um navegador, escolha o servidor e autorize o bot.
1. Será aberta uma tela de autorização
2. Escolha o servidor onde deseja adicionar o bot
3. Clique no botão "Continuar"
4. Na tela seguinte, certifique-se de que o bot esteja em um cargo (role) com permissões:
  - Ver canais
  - Opcionalmente, Enviar mensagens
  - Opcionalmente, Ver histórico de mensagens
  - Conectar (para canais de voz)

Não é necessário que o bot fale, apenas que **observe entradas e saídas**.
5. Clique no botão "Autorizar"

### 6. O bot tem permissão para monitorar os canais de voz

Verifique no Discord:

#### 6.1 O bot aparece na lista de membros?
1. No Discord, vá ao **servidor onde o bot foi adicionado**
2. No canto superior esquerdo, clique com o botão direito no nome do servidor → **"Configurações do servidor"**
2. Verifique se o bot aparece na lista de membros

#### **6.2 Verificar permissões da role (função)** atribuída ao bot

1. No Discord, vá ao **servidor onde o bot foi adicionado**
2. No canto superior esquerdo, clique com o botão direito no nome do servidor → **"Configurações do servidor"**
3. Vá em **"Cargos"** ou **"Funções" (Roles)**
4. Selecione a **role associada ao ClockifyBot**
5. Verifique se esta role tem as seguintes permissões **marcadas**:
   - **Visualizar Canais (View Channels)**
   - **Conectar (Connect)**
   - **Ler Histórico de Mensagens (Read Message History)** (se necessário)
   - **Enviar Mensagens (Send Messages)** (se desejar que ele registre logs no chat)

> ⚠️ Caso o bot **não tenha uma role** definida, adicione uma e atribua as permissões acima.


#### **6.3 Verificar permissões específicas no canal de voz**

Mesmo que a role tenha permissão global, o canal pode ter regras específicas. Para verificar:

1. Clique com o botão direito no **canal de voz** onde os usuários se conectam
2. Vá em **"Editar Canal"**
3. Acesse a aba **"Permissões"**
4. Verifique se a role do bot (ou o próprio bot, se estiver listado) tem:
   - **Ver Canal**
   - **Conectar**
   - (Não é necessário “Falar” ou “Transmitir vídeo”)

#### 6.4 **Verificar se o bot está no mesmo canal de voz**

Na prática:

- O bot **não entra no canal de voz** automaticamente, pois ele apenas **escuta eventos**.
- O que se deseja verificar é **se o evento `on_voice_state_update` é disparado** quando um usuário entra ou sai.

**Como verificar isso:**

1. Execute o bot (`docker logs -f` ou terminal local)
2. Entre com um usuário mapeado no canal de voz
3. O terminal deve exibir algo como:

```
[INFO] Usuário 123456789 entrou no canal de voz #Geral
[INFO] Iniciando timer no Clockify...
```

---

## Próximos passos para colocar o ClockifyBot em funcionamento

Agora que o bot está no servidor, é necessário garantir que:

### 1. O bot está **executando no ambiente de backend**

Verifique se o bot está rodando (em Docker ou localmente).

#### Se estiver usando Docker:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker-compose logs -f
```

#### Se estiver rodando localmente:

```bash
python run.py
```

> Certifique-se de que o arquivo `.env` esteja preenchido com:
```env
DISCORD_TOKEN=seu_token_do_bot
CLOCKIFY_API_KEY=sua_api_key
CLOCKIFY_WORKSPACE_ID=seu_workspace_id
CLOCKIFY_PROJECT_ID=opcional
```

E que `config/users_map.json` tenha o mapeamento correto:
```json
{
  "ID_DO_USUARIO_DISCORD": {
    "clockify_user_id": "ID_DO_USUARIO_CLOCKIFY"
  }
}
```



### 2. Realize um teste funcional

1. Com um usuário devidamente mapeado, entre em um canal de voz.
2. Verifique no painel do Clockify se foi iniciado um novo timer.
3. Saia do canal de voz e verifique se o timer foi parado.
4. Observe os logs no terminal para ver o comportamento do bot.


### 3. Monitorar erros (se houver)

- Se o timer **não iniciar**, verifique:
  - Logs do bot
  - Se o ID do usuário Discord está corretamente mapeado para o ID do Clockify
  - Se a API Key e o Workspace ID estão corretos

    

---
## Referências

- Discord Developer Portal: https://discord.com/developers
- Documentação do evento `on_voice_state_update`: https://discordpy.readthedocs.io/en/stable/api.html#discord.on_voice_state_update

