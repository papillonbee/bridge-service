from bridgepy.datastore import Datastore
from bridgepy.exception import BizException
from bridgepy.game import GameId, Game
from dataclasses import asdict
import jsons
import requests
from requests import Response


class GameAppSheetDatastore(Datastore[GameId, Game]):

    def __init__(self, app_id: str, table: str, app_access_key: str) -> None:
        self.url = f"https://www.appsheet.com/api/v2/apps/{app_id}/tables/{table}/Action"
        self.headers = {"applicationAccessKey": app_access_key}
        self.properties = {"Timezone": "Asia/Singapore"}

    def insert(self, game: Game) -> None:
        data = {
            "Action": "Add",
            "Properties": self.properties,
            "Rows": [
                {
                    "id": game.id.value,
                    "game": jsons.dumps(asdict(game)),
                }
            ]
        }
        response: Response = requests.post(self.url, headers = self.headers, json = data)
        if not response.ok:
            raise BizException(20001, f"insert game id: {game.id.value} failed with response: {response}")

    def update(self, game: Game) -> None:
        data = {
            "Action": "Edit",
            "Properties": self.properties,
            "Rows": [
                {
                    "id": game.id.value,
                    "game": jsons.dumps(asdict(game)),
                }
            ]
        }
        response: Response = requests.post(self.url, headers = self.headers, json = data)
        if not response.ok:
            raise BizException(20002, f"update game id: {game.id.value} failed with response: {response}")

    def delete(self, id: GameId) -> None:
        data = {
            "Action": "Delete",
            "Rows": [{"id": id.value}]
        }
        response: Response = requests.post(self.url, headers = self.headers, json = data)
        if not response.ok:
            raise BizException(20003, f"delete game id: {id.value} failed with response: {response}")

    def query(self, id: GameId) -> Game | None:
        data = {
            "Action": "Find",
            "Rows": [{"id": id.value}]
        }
        response: Response = requests.post(self.url, headers = self.headers, json = data)
        if not response.ok:
            raise BizException(20004, f"query game id: {id.value} failed with response: {response}")
        games = self.__parse_list(response)
        if len(games) == 0:
            return None
        return games[0]

    def __parse_list(self, response: Response) -> list[Game]:
        body = response.json()
        if type(body) is not list:
            return []
        return [jsons.load(jsons.loads(row["game"]), Game) for row in body]

class GameLocalDataStore(Datastore[GameId, Game]):

    def __init__(self) -> None:
        self.games: list[Game] = []

    def insert(self, game: Game) -> None:
        i = self.__query_index(game.id)
        if i is not None:
            return
        self.games.append(game)

    def update(self, game: Game) -> None:
        i = self.__query_index(game.id)
        if i is None:
            return
        self.games = self.games[:i] + [game] + self.games[i+1:]

    def delete(self, id: GameId) -> None:
        i = self.__query_index(id)
        if i is None:
            return
        self.games = self.games[:i] + self.games[i+1:]

    def query(self, id: GameId) -> Game | None:
        i = self.__query_index(id)
        if i is None:
            return None
        return self.games[i]

    def __query_index(self, id: GameId) -> int | None:
        for i in range(len(self.games)):
            if self.games[i].id == id:
                return i
        return None
