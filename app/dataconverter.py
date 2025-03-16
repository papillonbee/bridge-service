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

    def convert(self, data: GamePlayerSnapshot) -> GamePlayerSnapshotResponse:
        return GamePlayerSnapshotResponse(
            game_id = data.game_id.value,
            player_id = data.player_id.value,
            player_actions = data.player_actions,
            player_hand = [
                CardEnum(card.__repr__()) for card in data.player_hand.cards
            ],
            bids = [
                PlayerBid(
                    player_id = player_bid.player_id.value,
                    bid = None if player_bid.bid is None else BidEnum(player_bid.bid.__repr__())
                ) for player_bid in data.bids
            ],
            bid_winner = None if data.bid_winner is None else data.bid_winner.player_id.value,
            bid_level = None if data.bid_winner is None else data.bid_winner.bid.level,
            trump_suit = None if data.bid_winner is None else data.bid_winner.bid.suit,
            partner = None if data.partner is None else CardEnum(data.partner.__repr__()),
            partner_player_id = None if data.partner_player_id is None else data.partner_player_id.value,
            tricks = [
                GameTrick(
                    player_tricks = [
                        PlayerTrick(
                            player_id = player_trick.player_id.value,
                            trick = CardEnum(player_trick.trick.__repr__()),
                            won = game_trick.trick_winner(data.bid_winner.bid.suit) == player_trick.player_id
                                if game_trick.ready_for_trick_winner() else False,
                        ) for player_trick in game_trick.player_tricks
                    ]
                ) for game_trick in data.tricks],
            scores = [
                PlayerScore(
                    player_id = player_score.player_id.value,
                    score = player_score.score,
                    won = player_score.won,
                    voted = player_score.voted,
                ) for player_score in data.scores
            ],
            player_turn = None if data.player_turn is None else data.player_turn.value,
        )

class BidRequestBuilder(DataConverter[BidEnum, Bid | None]):
    
    def convert(self, data: BidEnum) -> Bid | None:
        return None if data == BidEnum.PASS else Bid.from_string(data.value)

@lru_cache
def get_game_snapshot_response_assembler() -> DataConverter[GamePlayerSnapshot, GamePlayerSnapshotResponse]:
    return GameSnapshotResponseAssembler()

@lru_cache
def get_bid_request_builder() -> DataConverter[BidEnum, Bid | None]:
    return BidRequestBuilder()
