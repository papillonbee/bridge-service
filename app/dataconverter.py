from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Generic, TypeVar
from bridgepy.game import GamePlayerSnapshot

from app.model import Bid, Card, GameTrick, PlayerBid, PlayerScore, PlayerTrick
from app.response import GamePlayerSnapshotResponse

T = TypeVar("T")
R = TypeVar("R")

class DataConverter(ABC, Generic[T, R]):

    @abstractmethod
    def convert(self, data: T) -> R:
        pass

class GameSnapshotDataConverter(DataConverter[GamePlayerSnapshot, GamePlayerSnapshotResponse]):

    def convert(self, game_player_snapshot: GamePlayerSnapshot) -> GamePlayerSnapshotResponse:
        return GamePlayerSnapshotResponse(
            game_id = game_player_snapshot.game_id.value,
            player_id = game_player_snapshot.player_id.value,
            player_action = game_player_snapshot.player_action,
            player_hand = [
                Card(card.__repr__()) for card in game_player_snapshot.player_hand.cards
            ],
            bids = [
                PlayerBid(
                    player_id = player_bid.player_id.value,
                    bid = None if player_bid.bid is None else Bid(player_bid.bid.__repr__())
                ) for player_bid in game_player_snapshot.bids
            ],
            bid_winner = None if game_player_snapshot.bid_winner is None else game_player_snapshot.bid_winner.value,
            partner = None if game_player_snapshot.partner is None else Card(game_player_snapshot.partner.__repr__()),
            tricks = [
                GameTrick(
                    player_tricks = [
                        PlayerTrick(
                            player_id = player_trick.player_id.value,
                            trick = Card(player_trick.trick.__repr__())
                        ) for player_trick in game_trick.player_tricks
                    ]
                ) for game_trick in game_player_snapshot.tricks],
            scores = [
                PlayerScore(
                    player_id = player_score.player_id.value,
                    score = player_score.score
                ) for player_score in game_player_snapshot.scores
            ],
        )

@lru_cache
def get_game_snapshot_data_converter() -> DataConverter[GamePlayerSnapshot, GamePlayerSnapshotResponse]:
    return GameSnapshotDataConverter()
