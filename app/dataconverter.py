from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Generic, TypeVar
from bridgepy.bid import Bid
from bridgepy.game import GamePlayerSnapshot

from app.model import BidEnum, CardEnum, GameTrick, PlayerBid, PlayerScore, PlayerTrick
from app.response import GamePlayerSnapshotResponse

T = TypeVar("T")
R = TypeVar("R")

class DataConverter(ABC, Generic[T, R]):

    @abstractmethod
    def convert(self, data: T) -> R:
        pass

class GameSnapshotResponseAssembler(DataConverter[GamePlayerSnapshot, GamePlayerSnapshotResponse]):

    def convert(self, game_player_snapshot: GamePlayerSnapshot) -> GamePlayerSnapshotResponse:
        return GamePlayerSnapshotResponse(
            game_id = game_player_snapshot.game_id.value,
            player_id = game_player_snapshot.player_id.value,
            player_action = game_player_snapshot.player_action,
            player_hand = [
                CardEnum(card.__repr__()) for card in game_player_snapshot.player_hand.cards
            ],
            bids = [
                PlayerBid(
                    player_id = player_bid.player_id.value,
                    bid = None if player_bid.bid is None else BidEnum(player_bid.bid.__repr__())
                ) for player_bid in game_player_snapshot.bids
            ],
            bid_winner = None if game_player_snapshot.bid_winner is None else game_player_snapshot.bid_winner.player_id.value,
            bid_level = None if game_player_snapshot.bid_winner is None else game_player_snapshot.bid_winner.bid.level,
            trump_suit = None if game_player_snapshot.bid_winner is None else game_player_snapshot.bid_winner.bid.suit,
            partner = None if game_player_snapshot.partner is None else CardEnum(game_player_snapshot.partner.__repr__()),
            partner_player_id = None if game_player_snapshot.partner_player_id is None else game_player_snapshot.partner_player_id.value,
            tricks = [
                GameTrick(
                    player_tricks = [
                        PlayerTrick(
                            player_id = player_trick.player_id.value,
                            trick = CardEnum(player_trick.trick.__repr__()),
                            won = game_trick.trick_winner(game_player_snapshot.bid_winner.bid.suit) == player_trick.player_id
                                if game_trick.ready_for_trick_winner() else False,
                        ) for player_trick in game_trick.player_tricks
                    ]
                ) for game_trick in game_player_snapshot.tricks],
            scores = [
                PlayerScore(
                    player_id = player_score.player_id.value,
                    score = player_score.score,
                    won = player_score.won,
                ) for player_score in game_player_snapshot.scores
            ],
            player_turn = None if game_player_snapshot.player_turn is None else game_player_snapshot.player_turn.value,
        )

class BidRequestBuilder(DataConverter[BidEnum, Bid | None]):
    
    def convert(self, bid: BidEnum) -> Bid | None:
        return None if bid == BidEnum.PASS else Bid.from_string(bid.value)

@lru_cache
def get_game_snapshot_response_assembler() -> DataConverter[GamePlayerSnapshot, GamePlayerSnapshotResponse]:
    return GameSnapshotResponseAssembler()

@lru_cache
def get_bid_request_builder() -> DataConverter[BidEnum, Bid | None]:
    return BidRequestBuilder()
