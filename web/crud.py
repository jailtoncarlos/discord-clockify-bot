from typing import TypeVar, Type, Optional, List, Any
from sqlmodel import SQLModel, Session, select
from sqlalchemy.orm import joinedload

from db.model_manager import ModelManager
from web.models import (
    ClockifyProject,
    DiscordChannel,
    ClockifyUser,
    UserProjectChannelBinding, UserNotification,
)


# Tipo genérico para os modelos
T = TypeVar("T", bound=SQLModel)


class CRUDManager(ModelManager):
    def get_by_id(self, model_class, id_value):
        """
        Retorna um único registro a partir de seu ID primário.

        Args:
            model_class (Type[SQLModel]): Classe do modelo SQLModel.
            id_value (Any): Valor da chave primária (geralmente 'id').

        Returns:
            SQLModel | None: Instância do modelo ou None se não encontrado.
        """
        return self.get_by_field(model_class, "id", id_value)

    def get_by_name(self, model_class, name_value: str):
        """
        Retorna um único registro a partir do campo 'name'.

        Args:
            model_class (Type[SQLModel]): Classe do modelo SQLModel.
            name_value (str): Valor do campo 'name'.

        Returns:
            SQLModel | None: Instância do modelo ou None se não encontrado.
        """
        return self.get_by_field(model_class, "name", name_value)

    def get_projects_by_workspace(self, workspace_id: str) -> List["ClockifyProject"]:
        """
        Retorna todos os projetos vinculados a um workspace específico.

        Args:
            workspace_id (str): ID do workspace Clockify.

        Returns:
            List[ClockifyProject]: Lista de projetos associados ao workspace.
        """
        return self.session.exec(
            select(ClockifyProject).where(ClockifyProject.workspace_id == workspace_id)
        ).all()

    def get_channels_by_server(self, server_id: str) -> List["DiscordChannel"]:
        """
        Retorna todos os canais de um servidor Discord.

        Args:
            server_id (str): ID do servidor.

        Returns:
            List[DiscordChannel]: Lista de canais associados ao servidor.
        """
        return self.session.exec(
            select(DiscordChannel).where(DiscordChannel.server_id == server_id)
        ).all()

    def get_users_by_project(self, project_id: str) -> List["ClockifyUser"]:
        """
        Retorna todos os usuários vinculados a um projeto específico do Clockify.

        Args:
            project_id (str): ID do projeto.

        Returns:
            List[ClockifyUser]: Lista de usuários associados ao projeto.
        """
        return self.session.exec(
            select(ClockifyUser).where(ClockifyUser.project_id == project_id)
        ).all()

    def get_clockify_user_by_discord_and_project(self, discord_user_id: str, project_id: str) -> ClockifyUser | None:
        """
        Retorna o usuário do Clockify (ClockifyUser) associado a um usuário do Discord e a um projeto específico.

        Args:
            discord_user_id (str): ID do usuário no Discord.
            project_id (str): ID do projeto no Clockify.

        Returns:
            ClockifyUser | None: O usuário do Clockify vinculado ao projeto e ao usuário do Discord, se existir.
        """
        binding = (
            self.session.query(UserProjectChannelBinding)
            .filter(
                UserProjectChannelBinding.discord_user_id == discord_user_id,
                UserProjectChannelBinding.discord_channel.has(DiscordChannel.project_id == project_id)
            )
            .first()
        )

        return binding.clockify_user if binding else None

    def has_been_notified(self, discord_user_id: str) -> bool:
        """
        Verifica se um usuário já foi notificado anteriormente.

        Args:
            discord_user_id (str): ID do usuário do Discord.

        Returns:
            bool: True se já foi notificado, False caso contrário.
        """
        stmt = select(UserNotification).where(UserNotification.user_id == discord_user_id)
        return self.session.exec(stmt).first() is not None

    def mark_as_notified(self, discord_user_id: str) -> None:
        """
        Marca um usuário como notificado, se ainda não estiver marcado.

        Args:
            discord_user_id (str): ID do usuário do Discord.
        """
        if not self.has_been_notified(discord_user_id):
            self.session.add(UserNotification(user_id=discord_user_id))
            self.session.commit()

    def get_first_binding_for_user(self, discord_user_id: str) -> UserProjectChannelBinding | None:
        """
        Retorna o primeiro vínculo encontrado entre um usuário do Discord e um canal/projeto.

        Args:
            discord_user_id (str): ID do usuário do Discord.

        Returns:
            UserProjectChannelBinding | None: Vínculo encontrado ou None.
        """
        statement = select(UserProjectChannelBinding).where(UserProjectChannelBinding.discord_user_id == discord_user_id)
        return self.session.exec(statement).first()

    def get_all_bindings_with_channel(self) -> list[UserProjectChannelBinding]:
        """
        Retorna todos os vínculos entre usuários e projetos, carregando os canais relacionados.

        Returns:
            List[UserProjectChannelBinding]: Lista de vínculos com canal carregado via joinedload.
        """
        return (
            self.session.query(UserProjectChannelBinding)
            .options(joinedload(UserProjectChannelBinding.discord_channel))
            .all()
        )

    def get_bindings_by_discord_user(self, discord_user_id: str) -> List["UserProjectChannelBinding"]:
        """
        Retorna todos os vínculos entre um usuário do Discord e canais/projetos.

        Args:
            discord_user_id (str): ID do usuário do Discord.

        Returns:
            List[UserProjectChannelBinding]: Lista de vínculos encontrados.
        """
        return self.session.exec(
            select(UserProjectChannelBinding).where(UserProjectChannelBinding.discord_user_id == discord_user_id)
        ).all()

    def get_project_bindings_for_user(self, discord_user_id: str) -> list[UserProjectChannelBinding]:
        """
        Retorna todos os vínculos de um usuário com canais e projetos associados,
        usando joins para evitar consultas adicionais.

        Args:
            discord_user_id (str): ID do usuário do Discord.

        Returns:
            List[UserProjectChannelBinding]: Lista de vínculos com canal e projeto pré-carregados.
        """
        return (
            self.session.query(UserProjectChannelBinding)
            .options(
                joinedload(UserProjectChannelBinding.discord_channel)
                .joinedload(DiscordChannel.project)
            )
            .filter(UserProjectChannelBinding.discord_user_id == discord_user_id)
            .all()
        )

    def get_bindings_by_user_and_server(self, discord_user_id: str, server_id: str):
        binding = (
            self.session.query(UserProjectChannelBinding)
            .filter(
                UserProjectChannelBinding.discord_user_id == discord_user_id,
                UserProjectChannelBinding.discord_channel.has(DiscordChannel.server_id == server_id)
            )
            .all()
        )
        return binding if binding else None