from quart import Quart, request, websocket
import keycloak as kc
import random, asyncpg, json
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="*")

connected_clients = {}

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

# TODO: websocket csatlakozás
@app.post("/rooms/<room_id>/join")
async def join_room_original(room_id):
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return {"error": "You need to be logged in to join a room."}, 403

    user_id = user["sub"]
    username = user["preferred_username"]

    # Megnézzük, hogy létezik-e a szoba az adatbázisban
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        return {"error": "Room not found."}, 404
    
    print("user_id:", user_id)
    print("username:", username)

    user_data = { user_id: {"name": username, "hand": [], "stack": [], "score": 0}}

    # Add user to the room's gamestate
    gamestate = json.loads(row["gamestate"])
    gamestate["players"].update(user_data)
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))
    
    return {"status": "ok", "room_id": row["room_id"]}

@app.websocket("/rooms/<room_id>/join")
async def join_room(room_id):
    user = await check_user_loggedin(websocket.headers.get("Authorization"))
    if user is None:
        return await websocket.send({ "status": "error", "msg": "You need to be logged in to join a room."})

    user_id = user["sub"]
    username = user["preferred_username"]

    # Megnézzük, hogy létezik-e a szoba az adatbázisban
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        return await websocket.send({ "status": "error", "msg": "Room not found."})

    user_data = { user_id: {"name": username, "hand": [], "stack": [], "score": 0}}

    # Add user to the room's gamestate
    gamestate = json.loads(row["gamestate"])
    gamestate["players"].update(user_data)
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    if not room_id in connected_clients:
        connected_clients[room_id] = set()

    connected_clients[room_id].add(websocket._get_current_object())

# TODO: websocket
@app.websocket("/rooms/<room_id>/leave")
async def leave_room(room_id):
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return await websocket.send({ "status": "error", "msg": "You need to be logged in to join a room."})
    
    user_id = user["sub"]

    # Megnézzük, hogy létezik-e a szoba az adatbázisban
    row = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", int(room_id))
    if not row:
        return await websocket.send({ "status": "error", "msg": "Room not found."})

    gamestate = json.loads(row["gamestate"])
    gamestate["players"].pop(user_id)
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    connected_clients
    return {"status": "ok"}

@app.delete("/rooms/<room_id>")
async def delete_room(room_id):
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return {"error": "You need to be logged in to join a room."}, 403
    
    await app.pool.execute("DELETE FROM rooms WHERE room_id = $1", int(room_id))

    return {"status": "ok"}

# @app.websocket("/ws")
# async def ws():
#     connected_clients.add(websocket._get_current_object())

#     try:
        

def run() -> None:
    app.run()

if __name__ == "__main__":
    run()
