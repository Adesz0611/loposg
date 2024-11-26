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
        "card_pool": ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4,
        "players": {},
        "cards": []
    }
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
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    # save user to a socketio room
    await sio.enter_room(sid, room_id)
    sio_rooms[sid] = {"user_id": user_id, "room_id": room_id}

    # send back that the join was successful
    await sio.emit("joined_room", {"room_id": row["room_id"]}, to=sid)

    # print the users in the room
    print("users in room: ", sio.rooms(sid))

    # send the other players that a new player joined with a player name
    await sio.emit("player_joined", {"player_name": username}, room=room_id)

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
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    # remove user from the socketio room
    await sio.leave_room(sid, room_id)
    sio_rooms.pop(sid)

    if not disconnect:
        # send back that the leave was successful
        await sio.emit("left_room", {"room_id": row["room_id"]}, to=sid)

    # check if the room is empty, if so, delete the room
    if not gamestate["players"]:
        await app.pool.execute("DELETE FROM rooms WHERE room_id = $1", int(room_id))
    else:
        # send the other players that a player left with a player name
        await sio.emit("player_left", {"player_name": username}, room=room_id)

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
