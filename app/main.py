from bridgebot.agent import BridgeAgent, BridgeRandomAgent
from bridgepy.bid import Bid
from bridgepy.bridge import BridgeClient
from bridgepy.card import Card
from bridgepy.datastore import Datastore
from bridgepy.exception import BizException
from bridgepy.game import Game, GameId, GamePlayerSnapshot
from bridgepy.player import PlayerId
from fastapi import FastAPI, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.client import GamePlayerBotClient
from app.config import get_settings
from app.dataconverter import get_bid_request_builder, get_game_snapshot_response_assembler, get_player_bot_response_assembler
from app.datastore import GameAppSheetDatastore, GameLocalDataStore, GamePlayerBotLocalDataStore
from app.entity import GamePlayerBot, PlayerBot
from app.request import BidRequest, CreateRequest, DeleteRequest, JoinRequest, PartnerRequest, ResetRequest, ToggleBotRequest, TrickRequest, ViewRequest
from app.response import BaseResponse, GamePlayerSnapshotResponse, PlayerBotResponse, SuccessResponse
from app.service import GameService
from app.websocket import GameWebSocketManager


settings = get_settings()
game_datastore: Datastore[GameId, Game] = GameAppSheetDatastore(
    settings.app_sheet_app_id,
    settings.app_sheet_game_table,
    settings.app_sheet_app_access_key,
) if settings.use_app_sheet else GameLocalDataStore()
bridge_client = BridgeClient(game_datastore)
game_socket_manager = GameWebSocketManager(bridge_client)

game_player_bot_datastore: Datastore[GameId, GamePlayerBot] = GamePlayerBotLocalDataStore()
game_player_bot_client = GamePlayerBotClient(game_player_bot_datastore)

bridge_agent: BridgeAgent = BridgeRandomAgent()
game_service = GameService(bridge_client, game_socket_manager, game_player_bot_client, bridge_agent, settings)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = [settings.cors_allow_origin],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

@app.post("/game/create", response_model_exclude_none = True)
async def create_game(request: CreateRequest) -> BaseResponse:
    await game_service.create_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse()

@app.post("/game/join", response_model_exclude_none = True)
async def join_game(request: JoinRequest) -> BaseResponse:
    await game_service.join_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse()

@app.post("/game/view", response_model_exclude_none = False)
async def view_game(request: ViewRequest) -> BaseResponse[GamePlayerSnapshotResponse]:
    snapshot: GamePlayerSnapshot = game_service.view_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse(data = get_game_snapshot_response_assembler().convert(snapshot))

@app.post("/game/bid", response_model_exclude_none = True)
async def bid(request: BidRequest) -> BaseResponse:
    bid: Bid | None = get_bid_request_builder().convert(request.bid)
    await game_service.bid(PlayerId(request.playerId), GameId(request.gameId), bid)
    return SuccessResponse()

@app.post("/game/partner", response_model_exclude_none = True)
async def choose_partner(request: PartnerRequest) -> BaseResponse:
    card: Card = Card.from_string(request.partner.value)
    await game_service.choose_partner(PlayerId(request.playerId), GameId(request.gameId), card)
    return SuccessResponse()

@app.post("/game/trick", response_model_exclude_none = True)
async def trick(request: TrickRequest) -> BaseResponse:
    card: Card = Card.from_string(request.trick.value)
    await game_service.trick(PlayerId(request.playerId), GameId(request.gameId), card)
    return SuccessResponse()

@app.post("/game/reset", response_model_exclude_none = True)
async def reset_game(request: ResetRequest) -> BaseResponse:
    await game_service.reset_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse()

@app.post("/game/delete", response_model_exclude_none = True)
async def delete_game(request: DeleteRequest) -> BaseResponse:
    await game_service.delete_game(GameId(request.gameId))
    return SuccessResponse()

@app.post("/game/bot", response_model_exclude_none = True)
async def toggle_bot(request: ToggleBotRequest) -> BaseResponse[PlayerBotResponse]:
    player_bot: PlayerBot = game_service.toggle_bot(PlayerId(request.playerId), GameId(request.gameId), request.toggle)
    return SuccessResponse(data = get_player_bot_response_assembler().convert(player_bot))

@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    return JSONResponse(content = {"code": exc.code, "msg": exc.msg})

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = exc.errors()[0]["msg"]
    return JSONResponse(content = {"code": 10000, "msg": error_msg})

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await game_service.handle_websocket(websocket, PlayerId(player_id), GameId(game_id))
