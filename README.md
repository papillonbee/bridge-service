# bridge-service
`bridge-service` is a [FastAPI](https://fastapi.tiangolo.com/) app providing 8 REST API's and 1 WebSocket for players to play floating bridge!

- `POST /game/create` Player can create a game
- `POST /game/join` Player can join the game
- `POST /game/view` Player can view the game's current state
    - already 4 players?
    - cards already dealt?
    - my bid turn?
    - my turn to choose partner?
    - my turn to trick?
    - can reset game?
- `POST /game/bid` Player can bid
- `POST /game/partner` Player who won the bid can choose partner
- `POST /game/trick` Player can trick
- `POST /game/reset` Player can reset game if game already concluded
- `POST /game/delete` Some upstream can delete the game after ended
- `WebSocket /ws/${gameId}/${playerId}` Player can chat and listen to latest game state change

---

## Dependencies
1. `bridge-service` is using Google Sheets through [AppSheet](https://about.appsheet.com/home/) as database (because it's free!) to manage `game` data
    - There's only 1 table with 2 columns
        - id `Text`, game ID
        - game `LongText`, game JSON object
    - This allows insert, update, query, and delete each game by game ID through [AppSheet API](https://support.google.com/appsheet/answer/10105398). From here, you will need to know 3 things to interact with the AppSheet API
        - App ID, go to your app in AppSheet > Settings > Integrations > App Id
        - Table name, same as your Google Sheets tab name
        - Application access key, go to your app in AppSheet > Settings > Integrations > Create Application Access Key
2. `bridge-service` is also using [`bridgepy`](https://github.com/papillonbee/bridgepy) package which provides features like create game, join game, view game, bid, choose partner, trick, and delete game!
    - `bridgepy==0.0.11` in requirements.txt

**TLDR**, the main logic to play floating bridge resides in [`bridgepy`](https://github.com/papillonbee/bridgepy) which revolves around `game` object and [AppSheet](https://about.appsheet.com/home/) is picked as the choice for database to manage `game` data in a centralized location so all 4 players can see the current state and interact with the `game` from single source

---

## Quick guide by cloning this project

After `git clone` this project to your local, you can do below

### Step 1: Create `.env` file with 6 environment variables
`APP_SHEET_APP_ID`, `APP_SHEET_GAME_TABLE`, and `APP_SHEET_APP_ACCESS_KEY` are used for interacting with the [AppSheet API](https://support.google.com/appsheet/answer/10105398) to manage `game` data

`USE_APP_SHEET` is used to enable/disable AppSheet API integration. Defaults to true. if put as false, will store `game` data in memory instead of Google Sheets

`CORS_ALLOW_ORIGIN` is used for whitelisting REST API request if request header `Origin` match with what's configured here. Defaults to `*` which means all origins are allowed

`WEBSOCKET_PING_INTERVAL` is used for WebSocket ping interval in seconds. Defaults to 20 seconds

Create it at project root directory

```
APP_SHEET_APP_ID=
APP_SHEET_GAME_TABLE=
APP_SHEET_APP_ACCESS_KEY=
USE_APP_SHEET=true
CORS_ALLOW_ORIGIN=*
WEBSOCKET_PING_INTERVAL=20
```

### Step 2: Run `bridge-service` container
From project root directory
```shell
podman-compose up --build -d
```

### Step 3: Read API doc at http://localhost:8000/redoc and try to create a game!
```curl
curl --location 'localhost:8000/game/create' \
--header 'Content-Type: application/json' \
--data '{
    "gameId": "1",
    "playerId": "111"
}'
```

### Step 4: Stop `bridge-service` container
From project root directory
```shell
podman-compose down
```

---

## Quick guide without cloning this project
Alternatively, you can also start your own project and pull `bridge-service` image directly from [Docker Hub](https://www.docker.com/products/docker-hub/) because I've uploaded it!

### Step 1: Create `.env` file with 6 environment variables
From your project root directory, create `.env` file same as above

### Step 2: Create your `docker-compose.yml` file
From your project root directory
```yml
version: "3.8"

services:
  bridge-service:
    image: ppllnb/bridge-service:latest
    ports:
      - "8000:80"
    env_file:
      - .env
    restart: always

```

### Step 3: Run your `bridge-service` container
From your project root directory
```shell
podman-compose up --build -d
```

### Step 4: Stop `bridge-service` container
From your project root directory
```shell
podman-compose down
```
