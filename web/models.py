from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List


class ClockifyWorkspace(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)

    projects: List["ClockifyProject"] = Relationship(back_populates="workspace")

class ClockifyProject(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    workspace_id: str = Field(foreign_key="clockifyworkspace.id")

    workspace: Optional[ClockifyWorkspace] = Relationship(back_populates="projects")
    users: List["ClockifyUser"] = Relationship(back_populates="project")
    channels: List["DiscordChannel"] = Relationship(back_populates="project")


class ClockifyUser(SQLModel, table=True):
    id: Optional[str] = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    api_key: str
    project_id: str = Field(foreign_key="clockifyproject.id")

    project: Optional[ClockifyProject] = Relationship(back_populates="users")
    account_links: List["UserProjectChannelBinding"] = Relationship(back_populates="clockify_user")


class DiscordServer(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)

    channels: List["DiscordChannel"] = Relationship(back_populates="server")
    users: List["DiscordUser"] = Relationship(back_populates="server")


class DiscordChannel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str = Field(nullable=False, unique=True)
    server_id: str = Field(foreign_key="discordserver.id")
    project_id: str = Field(foreign_key="clockifyproject.id")

    server: Optional[DiscordServer] = Relationship(back_populates="channels")
    project: Optional[ClockifyProject] = Relationship(back_populates="channels")
    account_links: list["UserProjectChannelBinding"] = Relationship(back_populates="discord_channel")


class DiscordUser(SQLModel, table=True):
    id: str = Field(primary_key=True)
    server_id: str = Field(foreign_key="discordserver.id")
    name: Optional[str] = None

    server: Optional[DiscordServer] = Relationship(back_populates="users")
    notifications: List["UserNotification"] = Relationship(back_populates="user")
    account_links: List["UserProjectChannelBinding"] = Relationship(back_populates="discord_user")


class UserNotification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="discorduser.id")

    user: Optional[DiscordUser] = Relationship(back_populates="notifications")


class UserProjectChannelBinding(SQLModel, table=True):
    # ID composto: "discord_user_id-discord_channel_id"
    id: str = Field(primary_key=True)

    discord_user_id: str = Field(foreign_key="discorduser.id")
    clockify_user_id: str = Field(foreign_key="clockifyuser.id")
    discord_channel_id: str = Field(foreign_key="discordchannel.id")

    # Relacionamentos
    discord_user: Optional["DiscordUser"] = Relationship(back_populates="account_links")
    clockify_user: Optional["ClockifyUser"] = Relationship(back_populates="account_links")
    discord_channel: Optional["DiscordChannel"] = Relationship()

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = f"{self.discord_user_id}-{self.discord_channel_id}"