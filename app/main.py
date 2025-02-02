from bridgepy.bid import Bid
from bridgepy.bridge import BridgeClient
from bridgepy.card import Card
from bridgepy.exception import BizException
from bridgepy.game import GameId
from bridgepy.player import PlayerId
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.dataconverter import get_game_snapshot_data_converter
from app.datastore import GameAppSheetDatastore
from app.request import BidRequest, CreateRequest, DeleteRequest, JoinRequest, PartnerRequest, TrickRequest, ViewRequest
from app.response import BaseResponse, GamePlayerSnapshotResponse, SuccessResponse


settings = get_settings()
game_datastore = GameAppSheetDatastore(settings.app_sheet_app_id, settings.app_sheet_game_table, settings.app_sheet_app_access_key)
bridge_client = BridgeClient(game_datastore)

app = FastAPI()

@app.post("/game/create", response_model_exclude_none = True)
async def create_game(request: CreateRequest) -> BaseResponse:
    bridge_client.create_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse()

@app.post("/game/join", response_model_exclude_none = True)
async def join_game(request: JoinRequest) -> BaseResponse:
    bridge_client.join_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse()

@app.post("/game/view", response_model_exclude_none = False)
async def view_game(request: ViewRequest) -> BaseResponse[GamePlayerSnapshotResponse]:
    game = bridge_client.view_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse(data = get_game_snapshot_data_converter().convert(game))

@app.post("/game/bid", response_model_exclude_none = True)
async def bid(request: BidRequest) -> BaseResponse:
    bridge_client.bid(PlayerId(request.playerId), GameId(request.gameId), None if request.bid is None else Bid.from_string(request.bid.value))
    return SuccessResponse()

@app.post("/game/partner", response_model_exclude_none = True)
async def choose_partner(request: PartnerRequest) -> BaseResponse:
    bridge_client.choose_partner(PlayerId(request.playerId), GameId(request.gameId), Card.from_string(request.partner.value))
    return SuccessResponse()

@app.post("/game/trick", response_model_exclude_none = True)
async def trick(request: TrickRequest) -> BaseResponse:
    bridge_client.trick(PlayerId(request.playerId), GameId(request.gameId), Card.from_string(request.trick.value))
    return SuccessResponse()

@app.post("/game/delete", response_model_exclude_none = True)
async def delete_game(request: DeleteRequest) -> BaseResponse:
    bridge_client.delete_game(GameId(request.gameId))
    return SuccessResponse()

@app.exception_handler(BizException)
async def unicorn_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    return JSONResponse(content = {"code": exc.code, "msg": exc.msg})
