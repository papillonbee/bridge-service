from bridgepy.player import PlayerAction
from typing import Generic, TypeVar

from app.model import Card, GameTrick, PlayerBid, PlayerScore, SnakeCaseModel


T = TypeVar("T")

class BaseResponse(SnakeCaseModel, Generic[T]):
    code: int
    msg: str
    data: T | None

class SuccessResponse(BaseResponse, Generic[T]):
    code: int = 0
    msg: str = "success"
    data: T | None = None

class GamePlayerSnapshotResponse(SnakeCaseModel):
    game_id: str
    player_id: str
    player_action: PlayerAction | None
    player_hand: list[Card]
    bids: list[PlayerBid]
    bid_winner: str | None
    partner: Card | None
    tricks: list[GameTrick]
    scores: list[PlayerScore]
