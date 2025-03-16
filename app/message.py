from enum import Enum

from app.model import SnakeCaseModel


class MessageType(Enum):
    CHAT = "CHAT"
    GAME = "GAME"
    PING = "PING"
    PONG = "PONG"

class Message(SnakeCaseModel):
    message_type: MessageType
    message: str | None = None
