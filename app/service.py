import asyncio
import logging
from bridgebot.agent import BridgeAgent
from bridgebot.env import BridgeEnv
from bridgebot.util import GameUtil
from bridgepy.bid import Bid
from bridgepy.bridge import BridgeClient
from bridgepy.card import Card
from bridgepy.game import Game, GameId, GamePlayerSnapshot
from bridgepy.player import PlayerId
from fastapi import WebSocket

from app.client import GamePlayerBotClient
from app.config import Settings
from app.entity import PlayerBot
from app.message import Message, MessageType
from app.websocket import GameWebSocketManager


logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

class GameService:

    def __init__(
        self,
        bridge_client: BridgeClient,
        game_socket_manager: GameWebSocketManager,
        game_player_bot_client: GamePlayerBotClient,
        bridge_agent: BridgeAgent,
        settings: Settings,
    ) -> None:
        self.bridge_client = bridge_client
        self.game_socket_manager = game_socket_manager
        self.game_player_bot_client = game_player_bot_client
        self.bridge_agent = bridge_agent
        self.settings = settings

    async def create_game(self, player_id: PlayerId, game_id: GameId) -> None:
        self.bridge_client.create_game(player_id, game_id)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
    
    async def join_game(self, player_id: PlayerId, game_id: GameId) -> None:
        self.bridge_client.join_game(player_id, game_id)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
        asyncio.create_task(self.auto_play(game_id))
    
    def view_game(self, player_id: PlayerId, game_id: GameId) -> GamePlayerSnapshot:
        return self.bridge_client.view_game(player_id, game_id)
    
    async def bid(self, player_id: PlayerId, game_id: GameId, bid: Bid | None) -> None:
        self.bridge_client.bid(player_id, game_id, bid)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
        asyncio.create_task(self.auto_play(game_id))
    
    async def choose_partner(self, player_id: PlayerId, game_id: GameId, card: Card) -> None:
        self.bridge_client.choose_partner(player_id, game_id, card)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
        asyncio.create_task(self.auto_play(game_id))
    
    async def trick(self, player_id: PlayerId, game_id: GameId, card: Card) -> None:
        self.bridge_client.trick(player_id, game_id, card)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
        asyncio.create_task(self.auto_play(game_id))
    
    async def reset_game(self, player_id: PlayerId, game_id: GameId) -> None:
        self.bridge_client.reset_game(player_id, game_id)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
        asyncio.create_task(self.auto_play(game_id))

    async def delete_game(self, game_id: GameId) -> None:
        self.bridge_client.delete_game(game_id)
        await self.game_socket_manager.broadcast_game_snapshot(game_id)
    
    def toggle_bot(self, player_id: PlayerId, game_id: GameId, toggle: bool | None) -> PlayerBot:
        return self.game_player_bot_client.toggle_bot(player_id, game_id, toggle)
    
    async def auto_play(self, game_id: GameId) -> None:
        game: Game = self.bridge_client.find_game(game_id)
        await self.__auto_play(game)
    
    async def __auto_play(self, game: Game) -> None:
        player_id: PlayerId | None = GameUtil.get_next_player_id(game)
        if player_id is None:
            return

        if not self.game_player_bot_client.is_bot(player_id, game.id):
            return

        if not game.dealt():
            return

        env = BridgeEnv(game)
        action = self.bridge_agent.predict(env._get_obs(player_id.value))
        _, _, dones, _, _ = env.step({player_id.value: action})

        self.bridge_client.game_datastore.update(game)
        await self.game_socket_manager.broadcast_game_snapshot(game.id)

        if dones["__all__"]:
            return
        await self.__auto_play(game)

    async def handle_websocket(self, websocket: WebSocket, player_id: PlayerId, game_id: GameId) -> None:
        await self.game_socket_manager.connect(websocket)
        last_pong_time = asyncio.get_event_loop().time()
        ping_task = None

        async def send_ping():
            nonlocal last_pong_time
            try:
                while True:
                    await asyncio.sleep(self.settings.websocket_ping_interval)
                    await self.game_socket_manager.send_personal_ping(websocket)
                    if asyncio.get_event_loop().time() - last_pong_time > self.settings.websocket_ping_interval * 2:
                        await websocket.close()
                        break
            except Exception:
                pass

        try:
            ping_task = asyncio.create_task(send_ping())
            await self.game_socket_manager.broadcast_message(f"{player_id.value} joins the chat", game_id)
            while True:
                text = await websocket.receive_text()
                try:
                    msg = Message.model_validate_json(text)
                except Exception:
                    continue
                if msg.message_type == MessageType.CHAT:
                    await self.game_socket_manager.broadcast_message(f"{player_id.value}: {msg.message}", game_id)
                if msg.message_type == MessageType.PONG:
                    last_pong_time = asyncio.get_event_loop().time()
        finally:
            self.game_socket_manager.disconnect(websocket)
            await self.game_socket_manager.broadcast_message(f"{player_id.value} left the chat", game_id)
            if ping_task is not None:
                ping_task.cancel()
                try:
                    await ping_task
                except asyncio.CancelledError:
                    pass
