from bridgepy.bridge import Datastore
from bridgepy.game import GameId
from bridgepy.player import PlayerId

from app.entity import GamePlayerBot, PlayerBot


class GamePlayerBotClient:

    def __init__(self, datastore: Datastore[GameId, GamePlayerBot]) -> None:
        self.datastore = datastore

    def toggle_bot(self, player_id: PlayerId, game_id: GameId, toggle: bool | None) -> PlayerBot:
        game_player_bot: GamePlayerBot | None = self.datastore.query(game_id)
        if game_player_bot is None:
            game_player_bot = GamePlayerBot(game_id, [])
            self.datastore.insert(game_player_bot)

        player_bot: PlayerBot | None = game_player_bot.find_player_bot(player_id)
        if player_bot is None:
            player_bot = PlayerBot(player_id)
            game_player_bot.add_player_bot(player_bot)
            self.datastore.update(game_player_bot)

        if toggle is None:
            return player_bot
 
        player_bot.bot = toggle
        game_player_bot.update_player_bot(player_bot)
        self.datastore.update(game_player_bot)

        return player_bot
    
    def is_bot(self, player_id: PlayerId, game_id: GameId) -> bool:
        game_player_bot: GamePlayerBot | None = self.datastore.query(game_id)
        if game_player_bot is None:
            return False

        player_bot: PlayerBot | None = game_player_bot.find_player_bot(player_id)
        if player_bot is None:
            return False

        return player_bot.bot
