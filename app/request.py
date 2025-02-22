from pydantic import BaseModel

from app.model import BidEnum, CardEnum


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
    bid: BidEnum

class PartnerRequest(GameRequest):
    partner: CardEnum

class TrickRequest(GameRequest):
    trick: CardEnum

class DeleteRequest(BaseRequest):
    gameId: str
