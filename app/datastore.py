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

    def insert(self, entity: Game) -> None:
        data = {
            "Action": "Add",
            "Properties": self.properties,
            "Rows": [
                {
                    "id": entity.id.value,
                    "game": jsons.dumps(asdict(entity)),
                }
            ]
        }
        response: Response = requests.post(self.url, headers = self.headers, json = data)
        if not response.ok:
            raise BizException(20001, f"insert game id: {entity.id.value} failed with response: {response}")

    def update(self, entity: Game) -> None:
        data = {
            "Action": "Edit",
            "Properties": self.properties,
            "Rows": [
                {
                    "id": entity.id.value,
                    "game": jsons.dumps(asdict(entity)),
                }
            ]
        }
        response: Response = requests.post(self.url, headers = self.headers, json = data)
        if not response.ok:
            raise BizException(20002, f"update game id: {entity.id.value} failed with response: {response}")

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
        self.games: dict[str, Game] = {}

    def insert(self, entity: Game) -> None:
        if self.query(entity.id) is not None:
            return
        self.games.update({entity.id.value: entity})

    def update(self, entity: Game) -> None:
        if self.query(entity.id) is None:
            return
        self.games.update({entity.id.value: entity})

    def delete(self, id: GameId) -> None:
        if self.query(id) is None:
            return
        self.games.pop(id.value)

    def query(self, id: GameId) -> Game | None:
        return self.games.get(id.value)
