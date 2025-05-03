from sqlmodel import Session
from db.database import engine, create_db_and_tables
from web.crud import CRUDManager
from web.models import *

from db.utils.cli_helpers import listar, buscar, criar, deletar  # ✅ Importa os utilitários CLI

def iniciar_shell():
    create_db_and_tables()  # Garante que o banco está pronto

    session = Session(engine)
    crud = CRUDManager(session)

    print("Shell interativo do banco iniciado.")
    print("Você pode usar as variáveis: `session`, `crud`, os modelos e os utilitários:")
    print(
        """\nExemplos de uso:
    listar(ClockifyUser)
    buscar(DiscordChannel, "1367634516944093214")
    criar(ClockifyWorkspace, id="test123", name="Workspace de Teste")
    deletar(ClockifyWorkspace, "test123")
    crud.get_all(ClockifyUser)
    crud.get_by_id(DiscordUser, "123456789")
    
    canal = crud.get_by_id(DiscordChannel, "1367634516944093214")
    print(canal.account_links)    
    
    link = crud.get_by_id(UserAccountLink, "594211442580783116-1367634516944093214")
    print(link.discord_channel)
    
"""
    )
    print("Digite `exit()` ou `Ctrl+D` para sair.\n")

    # Inicia shell interativo com contexto
    import code
    vars_contexto = globals().copy()
    vars_contexto.update(
        {
            "session": session,
            "crud": crud,
            # Modelos
            "ClockifyWorkspace": ClockifyWorkspace,
            "ClockifyProject": ClockifyProject,
            "ClockifyUser": ClockifyUser,
            "DiscordServer": DiscordServer,
            "DiscordChannel": DiscordChannel,
            "DiscordUser": DiscordUser,
            "UserAccountLink": UserProjectChannelBinding,
            "UserNotification": UserNotification,
            # Utilitários CLI
            "listar": lambda m: listar(crud, m),
            "buscar": lambda m, i: buscar(crud, m, i),
            "criar": lambda m, **kwargs: criar(crud, m, **kwargs),
            "deletar": lambda m, i: deletar(crud, session, m, i),
        }
    )
    code.interact(local=vars_contexto)

if __name__ == "__main__":
    iniciar_shell()
