import asyncio
from bridgepy.bid import Bid
from bridgepy.bridge import BridgeClient
from bridgepy.card import Card
from bridgepy.datastore import Datastore
from bridgepy.exception import BizException
from bridgepy.game import Game, GameId
from bridgepy.player import PlayerId
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketState

from app.config import get_settings
from app.dataconverter import get_bid_request_builder, get_game_snapshot_response_assembler
from app.datastore import GameAppSheetDatastore, GameLocalDataStore
from app.message import Message, MessageType
from app.request import BidRequest, CreateRequest, DeleteRequest, JoinRequest, PartnerRequest, ResetRequest, TrickRequest, ViewRequest
from app.response import BaseResponse, GamePlayerSnapshotResponse, SuccessResponse
from app.websocket import GameWebSocketManager


settings = get_settings()
game_datastore: Datastore[GameId, Game] = GameAppSheetDatastore(
    settings.app_sheet_app_id,
    settings.app_sheet_game_table,
    settings.app_sheet_app_access_key,
) if settings.use_app_sheet else GameLocalDataStore()
bridge_client = BridgeClient(game_datastore)
game_socket_manager = GameWebSocketManager(bridge_client)

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
    bridge_client.create_game(PlayerId(request.playerId), GameId(request.gameId))
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.post("/game/join", response_model_exclude_none = True)
async def join_game(request: JoinRequest) -> BaseResponse:
    bridge_client.join_game(PlayerId(request.playerId), GameId(request.gameId))
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.post("/game/view", response_model_exclude_none = False)
async def view_game(request: ViewRequest) -> BaseResponse[GamePlayerSnapshotResponse]:
    game = bridge_client.view_game(PlayerId(request.playerId), GameId(request.gameId))
    return SuccessResponse(data = get_game_snapshot_response_assembler().convert(game))

@app.post("/game/bid", response_model_exclude_none = True)
async def bid(request: BidRequest) -> BaseResponse:
    bid: Bid | None = get_bid_request_builder().convert(request.bid)
    bridge_client.bid(PlayerId(request.playerId), GameId(request.gameId), bid)
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.post("/game/partner", response_model_exclude_none = True)
async def choose_partner(request: PartnerRequest) -> BaseResponse:
    bridge_client.choose_partner(PlayerId(request.playerId), GameId(request.gameId), Card.from_string(request.partner.value))
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.post("/game/trick", response_model_exclude_none = True)
async def trick(request: TrickRequest) -> BaseResponse:
    bridge_client.trick(PlayerId(request.playerId), GameId(request.gameId), Card.from_string(request.trick.value))
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.post("/game/reset", response_model_exclude_none = True)
async def reset_game(request: ResetRequest) -> BaseResponse:
    bridge_client.reset_game(PlayerId(request.playerId), GameId(request.gameId))
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.post("/game/delete", response_model_exclude_none = True)
async def delete_game(request: DeleteRequest) -> BaseResponse:
    bridge_client.delete_game(GameId(request.gameId))
    await game_socket_manager.broadcast_game_snapshot(request.gameId)
    return SuccessResponse()

@app.exception_handler(BizException)
async def biz_exception_handler(request: Request, exc: BizException) -> JSONResponse:
    return JSONResponse(content = {"code": exc.code, "msg": exc.msg})

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    error_msg = exc.errors()[0]["msg"]
    return JSONResponse(content = {"code": 10000, "msg": error_msg})

@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await game_socket_manager.connect(websocket)
    last_pong_time = asyncio.get_event_loop().time()
    ping_task = None

    async def send_ping():
        nonlocal last_pong_time
        try:
            while True:
                await asyncio.sleep(get_settings().websocket_ping_interval)
                await game_socket_manager.send_personal_ping(websocket)
                if asyncio.get_event_loop().time() - last_pong_time > get_settings().websocket_ping_interval * 2:
                    await websocket.close()
                    break
        except Exception:
            pass

    try:
        ping_task = asyncio.create_task(send_ping())
        await game_socket_manager.broadcast_message(f"{player_id} joins the chat", game_id)
        while True:
            text = await websocket.receive_text()
            try:
                msg = Message.model_validate_json(text)
            except Exception:
                continue
            if msg.message_type == MessageType.CHAT:
                await game_socket_manager.broadcast_message(f"{player_id}: {msg.message}", game_id)
            if msg.message_type == MessageType.PONG:
                last_pong_time = asyncio.get_event_loop().time()
    finally:
        game_socket_manager.disconnect(websocket)
        await game_socket_manager.broadcast_message(f"{player_id} left the chat", game_id)
        if ping_task is not None:
            ping_task.cancel()
            try:
                await ping_task
            except asyncio.CancelledError:
                pass
