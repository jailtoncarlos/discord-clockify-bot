import logging
from discord import app_commands, Interaction, DMChannel
from discord.ext import commands
from sqlmodel import Session

from bot import clockify_client
from web.crud import CRUDManager
from db.database import engine
from web.models import DiscordChannel, ClockifyProject

logger = logging.getLogger(__name__)


class ClockifyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = Session(bind=engine)
        self.crud = CRUDManager(self.session)

    @app_commands.command(name="descricao", description="Atualiza a descrição do timer ativo no Clockify")
    @app_commands.describe(texto="Nova descrição da tarefa do clock en execução")
    async def atualizar_descricao(self, interaction: Interaction, texto: str):
        await interaction.response.defer(ephemeral=True)
        try:
            sucesso, mensagem = clockify_client.update_description(interaction.user, texto)
        except Exception as e:
            logger.exception("Erro ao atualizar a tarefa no Clockify")
            await interaction.followup.send("Erro interno ao atualizar a tarefa.", ephemeral=True)
            return
        await interaction.followup.send(mensagem, ephemeral=True)

    @app_commands.command(name="listar_tarefas", description="Lista as tarefas abertas no projeto associado ao canal ou ao ID informado.")
    @app_commands.describe(project_id="ID do projeto no Clockify (obrigatório se estiver usando o bot via DM)")
    async def listar_tarefas(self, interaction: Interaction, project_id: str):
        await interaction.response.defer(ephemeral=True)
        channel_id = str(interaction.channel_id)
        channel_name = getattr(interaction.channel, "name", "DM")

        project = self.crud.get_by_id(ClockifyProject, project_id)
        if not project:
            await interaction.followup.send(
                f"Projeto com ID `{project_id}` não encontrado.",
                ephemeral=True
            )
            logger.error(f"Projeto {project_id} não encontrado via DM.")
            return

        if not isinstance(interaction.channel, DMChannel):
            canal = self.crud.get_by_id(DiscordChannel, channel_id)
            if not canal:
                await interaction.followup.send("Este canal não está vinculado a nenhum projeto.")
                logger.error(f"Canal {channel_name} ({channel_id}) não associado a nenhum projeto Clockify.")
                return

            project = self.crud.get_by_id(ClockifyProject, canal.project_id)
            if not project:
                await interaction.followup.send("O projeto vinculado a este canal não foi encontrado.")
                logger.error(f"Projeto {canal.project_id} não encontrado para canal {channel_id}.")
                return

        try:
            discord_user_id = str(interaction.user.id)
            sucesso, mensagem = clockify_client.list_tasks(discord_user_id, project)
        except Exception as e:
            logger.exception("Erro ao listar tarefas no Clockify")
            await interaction.followup.send("Erro interno ao listar tarefas.", ephemeral=True)
            return
        await interaction.followup.send(mensagem, ephemeral=True)

    @app_commands.command(name="usar_tarefa", description="Associa uma tarefa existente ao timer aivo")
    @app_commands.describe(task_id="ID da tarefa no Clockify")
    async def usar_tarefa(self, interaction: Interaction, task_id: str):
        await interaction.response.defer(ephemeral=True)
        try:
            sucesso, mensagem = clockify_client.associate_task(interaction.user, task_id)
        except Exception as e:
            logger.exception("Erro ao associar a tarefa no Clockify")
            await interaction.followup.send("Erro interno ao associar a tarefa.", ephemeral=True)
            return
        await interaction.followup.send(mensagem, ephemeral=True)

    @app_commands.command(name="meus_projetos", description="Lista os projetos do Clockify vinculados a você")
    async def meus_projetos(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            user_id = str(interaction.user.id)

            bindings = self.crud.get_project_bindings_for_user(user_id)

            logger.debug(f"Listando projetos do usuário {interaction.user.display_name} ({user_id})...")

            if not bindings:
                await interaction.followup.send("Nenhum projeto vinculado a seu usuário no Discord.")
                logger.warning(f"Usuário {user_id} não vinculado a nenhum projeto.")
                return

            mensagens = []
            for binding in bindings:
                projeto = binding.discord_channel.project
                if projeto:
                    mensagens.append(f"• {projeto.name or '(sem nome)'} (ID: `{projeto.id}`)\n")
                    logger.debug(f"Projeto encontrado: {projeto.name} ({projeto.id})")

            if not mensagens:
                await interaction.followup.send("Nenhum projeto encontrado para os vínculos existentes.")
                logger.warning(f"Usuário {user_id} não vinculado a nenhum projeto válido.")
            else:
                await interaction.followup.send(
                    "**Projetos vinculados ao seu usuário:**\n" + "\n".join(mensagens),
                    ephemeral=True
                )
                logger.info(f"Projetos vinculados enviados para {interaction.user.display_name} ({user_id})")

        except Exception:
            logger.exception("Erro inesperado ao listar projetos do usuário.")
            await interaction.followup.send("Erro interno ao buscar seus projetos.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ClockifyCommands(bot))
