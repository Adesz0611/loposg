from quart import Quart, request, websocket
import keycloak as kc
import random, asyncpg, json
from quart_cors import cors
import socketio

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins=["http://localhost:3000"])
app = Quart(__name__)
app = cors(app, allow_origin="*")
asgi_app = socketio.ASGIApp(sio, app)


sio_rooms = {}
user_id2sid = {}

openid = kc.KeycloakOpenID(server_url="http://localhost:8080/",
                           client_id="loposg",
                           realm_name="master",
                           client_secret_key="HAJQtPl0W5OOjxoSjXuqvgF1xyXOdDwD",
)

async def check_user_loggedin(token):
    try:
        user = await openid.userinfo(token)
        return user
    except kc.KeycloakAuthenticationError:
        return None
    
def generate_gamestate():
    template = {
        "card_pool": ['HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK',
                      'TA', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'TJ', 'TQ', 'TK',
                      'CA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'CJ', 'CQ', 'CK',
                      'PA', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10', 'PJ', 'PQ', 'PK',],
        "players": {},
        "cards": [],
        "started": False,
        "player_order": [],
        "current_player": 0, # it is an index of the players list
    }

    # TODO: more complex card pool generation
    random.shuffle(template["card_pool"])
    return template

@app.before_serving
async def create_db_pool():
    app.pool = await asyncpg.create_pool(user="loposg", password="loposg123", database="loposg", host="localhost")

ROOM_LIMIT = 100

async def generate_room_id(room_ids):
    while True:
        room_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if room_id not in room_ids:
            return room_id

@app.get("/login")
async def login():
    auth_url = await openid.auth_url("http://localhost:3000/", scope="email profile openid")
    return {"auth_url": auth_url}

@app.post("/callback")
async def callback():
    data = await request.get_json()
    code = data.get("code")
    print(code)
    token = await openid.token(code=code, grant_type="authorization_code", redirect_uri="http://localhost:3000/")
    user_info = await openid.userinfo(token["access_token"])
    return {"user_info": user_info, "token": token}

@app.post("/logout")
async def logout():
    data = await request.get_json()
    token = data.get("token_refresh")
    await openid.logout(token)
    return {"status": "ok"}

@app.post("/rooms")
async def create_room():
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return {"error": "You need to be logged in to create a room."}, 403

    # Megnézzük, hogy létre tudunk-e hozni szobát (nem értük el a limitet)
    room_ids = await app.pool.fetch("SELECT room_id FROM rooms")
    room_ids = {str(x["room_id"]) for x in room_ids}
    if len(room_ids) >= ROOM_LIMIT:
        return {"error": "Room limit reached."}, 403

    room_id = await generate_room_id(room_ids)

    await app.pool.execute("""
INSERT INTO rooms (room_id, gamestate) VALUES ($1, $2)
""", int(room_id), json.dumps(generate_gamestate()))

    return {"room_id": room_id}

# rooms = {
#     "123456": {
#         "main_deck": ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4,
#         "users": {1: {"name": "Alice", "hand": [], "stack": [], "score": 0},
#                   2: {"name": "Bob", "hand": [], "stack": [], "score": 0},
#                   3: {"name": "Charlie", "hand": [], "stack": [], "score": 0},
#                   4: {"name": "David", "hand": [], "stack": [], "score": 0}},
#     }
# }


@app.get("/rooms")
async def fetch_rooms():
    room_ids = await app.pool.fetch("SELECT room_id FROM rooms")
    room_ids = [str(x["room_id"]) for x in room_ids]
    return {"rooms": room_ids}

@sio.event
async def connect(sid, environ):
    print("connect ", sid)

@sio.on("join_room")
async def join_room(sid, data):
    print("raw data: ", data)
    bearer = data["bearer"]
    room_id = data["room_id"]

    # check if room_id defined and not empty
    if not room_id:
        await sio.emit("error", {"msg": "Room ID is required"}, to=sid)
        return

    # check if room_id is in the database
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        await sio.emit("error", {"msg": "Room not found."}, to=sid)
        return
    
    user = await check_user_loggedin(bearer)
    if user is None:
        await sio.emit("error", {"msg": "You need to be logged in to join a room."}, to=sid)
        return
    
    user_id = user["sub"]
    username = user["preferred_username"]

    user_data = { user_id: {"name": username, "hand": [], "stack": [], "score": 0}}

    # Add user to the room's gamestate
    gamestate = json.loads(row["gamestate"])
    gamestate["players"].update(user_data)
    gamestate["player_order"].append(user_id)
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    # save user to a socketio room
    await sio.enter_room(sid, room_id)
    sio_rooms[sid] = {"user_id": user_id, "room_id": room_id}
    user_id2sid[user_id] = sid

    # send back that the join was successful
    await sio.emit("joined_room", {"room_id": row["room_id"]}, to=sid)

    # print the users in the room
    print("users in room: ", sio.rooms(sid))

    # send the other players that a new player joined with a player name
    await sio.emit("player_joined", {"player_name": username}, room=room_id)

    # send the other players the new player order
    await sio.emit("player_order", {"player_order": gamestate["player_order"]}, room=room_id)

# Start a game
@sio.on("start_game")
async def start_game(sid, data):
    if sid not in sio_rooms:
        await sio.emit("error", {"msg": "You are not in a room."}, to=sid)
        return

    room_id = sio_rooms[sid]["room_id"]
    user_id = sio_rooms[sid]["user_id"]

    # check if room_id is in the database
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        await sio.emit("error", {"msg": "Room not found."}, to=sid)
        return

    gamestate = json.loads(row["gamestate"])

    # check if the room has enough players
    if len(gamestate["players"]) < 2:
        await sio.emit("error", {"msg": "Not enough players to start the game."}, to=sid)
        return

    # check if the game has already started
    if gamestate.get("started", False):
        await sio.emit("error", {"msg": "Game already started."}, to=sid)
        return

    # shuffle the card pool
    random.shuffle(gamestate["card_pool"])

    # deal the cards to the players
    for player_id in gamestate["players"]:
        gamestate["players"][player_id]["hand"] = gamestate["card_pool"][:5]
        gamestate["card_pool"] = gamestate["card_pool"][5:]

    # set the game as started
    gamestate["started"] = True

    # save the gamestate
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    # send the gamestate to the players
    for player_id in gamestate["players"]:
        await sio.emit("own_gamestate", gamestate["players"][player_id], to=user_id2sid[player_id])

    global_gamestate = {
        "current_player": gamestate["current_player"],
        "main_deck": gamestate["cards"],
    }

    global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-2:] for player_id in gamestate["player_order"]]

    await sio.emit("global_gamestate", global_gamestate, room=room_id)

@sio.on("card_action")
async def card_action(sid, data):
    if sid not in sio_rooms:
        await sio.emit("error", {"msg": "You are not in a room."}, to=sid)
        return
    
    room_id = sio_rooms[sid]["room_id"]

    # check if room_id is in the database
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        await sio.emit("error", {"msg": "Room not found."}, to=sid)
        return
    
    gamestate = json.loads(row["gamestate"])
    user_id = sio_rooms[sid]["user_id"]

    # check if the game has started
    if not gamestate.get("started", False):
        await sio.emit("error", {"msg": "Game has not started yet."}, to=sid)
        return
    
    # check if it is the player's turn
    if gamestate["player_order"][gamestate["current_player"]] != user_id:
        await sio.emit("error", {"msg": "Not your turn."}, to=sid)
        return
    
    if "action" not in data:
        await sio.emit("error", {"msg": "Action is required."}, to=sid)
        return
    
    action = data["action"]

    if action == "throw":
        action_throw(sid, data, gamestate, user_id, room_id)
    elif action == "pair":
        action_pair(sid, data, gamestate, user_id, room_id)

async def action_throw(sid, data, gamestate, user_id, room_id):
    if "card" not in data:
        await sio.emit("error", {"msg": "Card is required."}, to=sid)
        return

    card = data["card"]
    if card not in gamestate["players"][user_id]["hand"]:
        await sio.emit("error", {"msg": "You don't have this card."}, to=sid)
        return

    gamestate["players"][user_id]["hand"].remove(card)
    gamestate["cards"].append(card)
    gamestate["current_player"] = (gamestate["current_player"] + 1) % len(gamestate["player_order"])
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    global_gamestate = {
        "current_player": gamestate["current_player"],
        "main_deck": gamestate["cards"],
    }
    global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-2:] for player_id in gamestate["player_order"]]
    await sio.emit("global_gamestate", global_gamestate, room=room_id)

    for player_id in gamestate["players"]:
        await sio.emit("own_gamestate", gamestate["players"][player_id], to=user_id2sid[player_id])

async def action_pair(sid, data, gamestate, user_id, room_id):
    if "cards" not in data or len(data["cards"]) != 2:
        await sio.emit("error", {"msg": "Two cards are required."}, to=sid)
        return

    card1, card2 = data["cards"]
    if card1 not in gamestate["players"][user_id]["hand"] or card2 not in gamestate["players"][user_id]["hand"]:
        await sio.emit("error", {"msg": "You don't have these cards."}, to=sid)
        return

    if card1[:-1] != card2[:-1]:  # Assuming card format is like 'HA', 'H2', etc.
        await sio.emit("error", {"msg": "Cards are not a pair."}, to=sid)
        return

    gamestate["players"][user_id]["hand"].remove(card1)
    gamestate["players"][user_id]["hand"].remove(card2)
    gamestate["players"][user_id]["stack"].extend([card1, card2])
    gamestate["current_player"] = (gamestate["current_player"] + 1) % len(gamestate["player_order"])
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    global_gamestate = {
        "current_player": gamestate["current_player"],
        "main_deck": gamestate["cards"],
    }
    global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-2:] for player_id in gamestate["player_order"]]
    await sio.emit("global_gamestate", global_gamestate, room=room_id)

    for player_id in gamestate["players"]:
        await sio.emit("own_gamestate", gamestate["players"][player_id], to=user_id2sid[player_id])

async def leave_room_fv(sid, disconnect=False):
    if sid not in sio_rooms:
        await sio.emit("error", {"msg": "You are not in a room."}, to=sid)
        return

    room_id = sio_rooms[sid]["room_id"]
    user_id = sio_rooms[sid]["user_id"]

    # check if room_id is in the database
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        await sio.emit("error", {"msg": "Room not found."}, to=sid)
        return

    # Remove user from the room's gamestate
    gamestate = json.loads(row["gamestate"])
    print("gamestate: ", gamestate)
    print("user_id: ", user_id)
    username = gamestate["players"][user_id]["name"]
    gamestate["players"].pop(user_id)
    gamestate["player_order"].remove(user_id)
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    # remove user from the socketio room
    await sio.leave_room(sid, room_id)
    sio_rooms.pop(sid)
    user_id2sid.pop(user_id)

    if not disconnect:
        # send back that the leave was successful
        await sio.emit("left_room", {"room_id": row["room_id"]}, to=sid)

    # check if the room is empty, if so, delete the room
    if not gamestate["players"]:
        await app.pool.execute("DELETE FROM rooms WHERE room_id = $1", int(room_id))
    else:
        # send the other players that a player left with a player name
        await sio.emit("player_left", {"player_name": username}, room=room_id)
        await sio.emit("player_order", {"player_order": gamestate["player_order"]}, room=room_id)

@sio.on("leave_room")
async def leave_room(sid, data):
    leave_room_fv(sid)

@sio.event
async def disconnect(sid):
    if sid in sio_rooms:
        await leave_room_fv(sid, True)
    print("disconnect ", sid)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=5000)
