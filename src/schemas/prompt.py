from enum import Enum

from pydantic import BaseModel


class AllowedRoleEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    role: AllowedRoleEnum
    content: str
