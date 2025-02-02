from bridgepy.card import Card
from pydantic import BaseModel

from app.model import Bid, Card


class BaseRequest(BaseModel):
    pass

class GameRequest(BaseRequest):
    gameId: str
    playerId: str

class CreateRequest(GameRequest):
    pass

class JoinRequest(GameRequest):
    pass

class ViewRequest(GameRequest):
    pass

class BidRequest(GameRequest):
    bid: Bid | None = None

class PartnerRequest(GameRequest):
    partner: Card

class TrickRequest(GameRequest):
    trick: Card

class DeleteRequest(BaseRequest):
    gameId: str
