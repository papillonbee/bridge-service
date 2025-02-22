# bridge-service
`bridge-service` is a [FastAPI](https://fastapi.tiangolo.com/) app providing 7 API's for players to play floating bridge!

- `POST /game/create` Player can create a game
- `POST /game/join` Player can join the game
- `POST /game/view` Player can view the game's current state
    - already 4 players?
    - cards already dealt?
    - my bid turn?
    - my turn to choose partner?
    - my turn to trick?
- `POST /game/bid` Player can bid
- `POST /game/partner` Player who won the bid can choose partner
- `POST /game/trick` Player can trick
- `POST /game/delete` Some upstream can delete the game after ended

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
    - `bridgepy==0.0.8` in requirements.txt

**TLDR**, the main logic to play floating bridge resides in [`bridgepy`](https://github.com/papillonbee/bridgepy) which revolves around `game` object and [AppSheet](https://about.appsheet.com/home/) is picked as the choice for database to manage `game` data in a centralized location so all 4 players can see the current state and interact with the `game` from single source

---

## Quick guide by cloning this project

After `git clone` this project to your local, you can do below

### Step 1: Create `.env` file with 4 environment variables
The first 3 are used for interacting with the [AppSheet API](https://support.google.com/appsheet/answer/10105398) to manage `game` data

The fourth variable is used for whitelisting request if request header `Origin` match with what's configured here

Create it at project root directory

```
APP_SHEET_APP_ID=
APP_SHEET_GAME_TABLE=
APP_SHEET_APP_ACCESS_KEY=
ALLOW_ORIGIN=
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

### Step 1: Pull latest `bridge-service` image from [Docker Hub](https://www.docker.com/products/docker-hub/)

```shell
podman pull docker.io/ppllnb/bridge-service:latest
```

### Step 2: Create `.env` file with 4 environment variables
From your project root directory, create `.env` file same as above

### Step 3: Create your `docker-compose.yml` file
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

### Step 4: Run your `bridge-service` container
From your project root directory
```shell
podman-compose up --build -d
```

### Step 5: Stop `bridge-service` container
From your project root directory
```shell
podman-compose down
```
