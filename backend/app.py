from quart import Quart, request
import keycloak as kc
import random, asyncpg, json
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="*")

openid = kc.KeycloakOpenID(server_url="http://localhost:8080/",
                           client_id="loposg",
                           realm_name="master",
                           client_secret_key="M8fQJjPAPE23JaFejL1XrIsagv75PS58",
)

async def check_user_loggedin(token):
    try:
        user = await openid.userinfo(token)
        return user
    except kc.KeycloakAuthenticationError:
        return None

ROOM_LIMIT = 100
rooms = {}

def generate_room_id():
    while True:
        room_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if room_id not in rooms:
            return room_id

async def generate_gamestate():
    template = {
        "card_pool": ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4,
        "players": [],
        "cards": []
    }
    return template

@app.before_serving
async def create_db_pool():
    app.pool = await asyncpg.create_pool(user="loposg", password="loposg123", database="loposg", host="localhost")

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

@app.post("/create_room")
async def create_room():
    gamestate = { "players": [], "cards": []}
    
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return {"error": "You need to be logged in to create a room."}, 403

    if len(rooms) >= ROOM_LIMIT:
        return {"error": "Room limit reached."}, 403

    room_id = generate_room_id()
    rooms[room_id] = {}
    gamestate = await generate_gamestate()
    await app.pool.execute("INSERT INTO rooms (room_id, gamestate) VALUES ($1, $2)", room_id, json.dumps(gamestate))
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
    return {"rooms": rooms}

@app.post("/join_room")
async def join_room():
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return {"error": "You need to be logged in to join a room."}, 403

    data = await request.get_json()
    room_id = data.get("room_id")
    if room_id not in rooms:
        return {"error": "Room not found."}, 404
    room = await app.pool.fetchrow("SELECT * FROM rooms WHERE room_id = $1", room_id)
    if room is None:
        return {"error": "Room not found."}, 404
    gamestate = json.loads(room["gamestate"])
    if len(gamestate["players"]) >= 4:
        return {"error": "Room is full."}, 403
    player_obj = {"name": user["preferred_username"], "hand": [], "stack": [], "score": 0, "id" : user["sub"]}
    gamestate["players"].append(player_obj)
    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), room_id)
    return {"status": "ok", "room_id": room_id}

def run() -> None:
    app.run()

if __name__ == "__main__":
    run()
