from bridgepy.bridge import BridgeClient
from bridgepy.game import Game, GameId, GamePlayerSnapshot
from bridgepy.player import PlayerId
from fastapi import WebSocket
import logging

from app.dataconverter import get_game_snapshot_response_assembler
from app.message import Message, MessageType


logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

class GameWebSocketManager:

    def __init__(self, bridge_client: BridgeClient):
        self.bridge_client = bridge_client
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        path_params = websocket.scope.get("path_params")
        logger.info(f"websocket.scope.path_params = {path_params}")
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        msg: str = Message(message_type = MessageType.CHAT, message = message).model_dump_json(by_alias = True)
        await websocket.send_text(msg)
    
    async def send_personal_ping(self, websocket: WebSocket):
        msg: str = Message(message_type = MessageType.PING).model_dump_json(by_alias = True, exclude_none = True)
        await websocket.send_text(msg)

    async def broadcast_message(self, message: str, game_id: str):
        for connection in self.active_connections:
            path_params = connection.scope.get("path_params")
            if path_params is None:
                logger.error(f"path_params not found in scope: {connection.scope}")
                continue
            if path_params.get("game_id") != game_id:
                continue
            msg: str = Message(message_type = MessageType.CHAT, message = message).model_dump_json(by_alias = True)
            await connection.send_text(msg)
    
    async def broadcast_game_snapshot(self, game_id: str):
        if len(self.active_connections) == 0:
            return
        game: Game = self.bridge_client.find_game(GameId(game_id))
        for connection in self.active_connections:
            path_params = connection.scope.get("path_params")
            if path_params is None:
                logger.error(f"path_params not found in scope: {connection.scope}")
                continue
            if path_params.get("game_id") != game_id:
                continue
            player_id = path_params.get("player_id")
            game_snapshot: GamePlayerSnapshot = game.player_snapshot(PlayerId(player_id))
            message: str = get_game_snapshot_response_assembler().convert(game_snapshot).model_dump_json(by_alias = True)
            msg: str = Message(message_type = MessageType.GAME, message = message).model_dump_json(by_alias = True)
            await connection.send_text(msg)
