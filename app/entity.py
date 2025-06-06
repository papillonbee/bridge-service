from bridgepy.entity import Entity
from bridgepy.game import GameId
from bridgepy.player import PlayerId
from dataclasses import dataclass


@dataclass
class PlayerBot:
    player_id: PlayerId
    bot: bool = False

@dataclass
class GamePlayerBot(Entity[GameId]):
    id: GameId
    player_bots: list[PlayerBot]

    def find_player_bot(self, player_id: PlayerId) -> PlayerBot | None:
        for player_bot in self.player_bots:
            if player_bot.player_id == player_id:
                return player_bot
        return None
    
    def add_player_bot(self, player_bot: PlayerBot) -> None:
        if self.find_player_bot(player_bot.player_id) is not None:
            return
        self.player_bots.append(player_bot)
    
    def update_player_bot(self, player_bot: PlayerBot) -> None:
        existing: PlayerBot | None = self.find_player_bot(player_bot.player_id)
        if existing is None:
            return
        existing.bot = player_bot.bot
