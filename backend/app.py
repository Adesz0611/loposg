from quart import Quart, request, jsonify, websocket
from .keycloak_openid import KeycloakOpenID, KeycloakPostError, KeycloakAuthenticationError
import random  # Ha használod
import asyncpg  # Itt importáljuk az asyncpg modult
import json
from quart_cors import cors

app = Quart(__name__)
app = cors(app, allow_origin="http://localhost:3000")

# Konfigurációs adatok
SERVER_URL = "http://localhost:8080"
REALM_NAME = "master"  # Cseréld le a saját realm nevedre
CLIENT_ID = "loposg"
CLIENT_SECRET_KEY = "M8fQJjPAPE23JaFejL1XrIsagv75PS58"  # Cseréld le a saját client secret-edre

# Keycloak OpenID kliens objektum létrehozása (még nincs session)
keycloak_openid = KeycloakOpenID(
    server_url=SERVER_URL,
    realm_name=REALM_NAME,
    client_id=CLIENT_ID,
    client_secret_key=CLIENT_SECRET_KEY,
    verify=False  # Éles környezetben állítsd True-ra
)

@app.before_serving
async def startup():
    """Az alkalmazás indítása előtt lefutó aszinkron metódus."""
    await keycloak_openid.init_session()

@app.after_serving
async def shutdown():
    """Az alkalmazás leállításakor lefutó aszinkron metódus."""
    await keycloak_openid.close_session()

@app.route('/callback', methods=['POST'])
async def callback():
    data = await request.json
    code = data.get('code')
    if not code:
        return jsonify({"error": "Code not provided"}), 400

    try:
        token_response = await keycloak_openid.token(
            grant_type="authorization_code",
            code=code,
            redirect_uri="http://localhost:3000/callback",
            client_secret_key=CLIENT_SECRET_KEY  # Ez a sor hozzáadása szükséges
        )
        return jsonify(token_response), 200
    except KeycloakPostError as e:
        app.logger.error(f"Hiba a token cseréje során: {e}")
        return jsonify({"error": "invalid_grant", "error_description": "Code not valid"}), 500

async def check_user_loggedin(token):
    try:
        user_info = await keycloak_openid.userinfo(token)
        return user_info
    except KeycloakAuthenticationError:
        return None

ROOM_LIMIT = 100
rooms = {}

def generate_room_id():
    while True:
        room_id = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        if room_id not in rooms:
            rooms[room_id] = {
                "gamestate": None,
                "clients": set()
            }
            return room_id

async def generate_gamestate():
    template = {
        "card_pool": ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4,
        "players": [],
        "cards": []
    }
    random.shuffle(template["card_pool"])
    return template

@app.before_serving
async def create_db_pool():
    app.pool = await asyncpg.create_pool(user="loposg", password="loposg123", database="loposg", host="localhost")

@app.get("/login")
async def login():
    # Az auth URL összeállítása manuálisan
    auth_url = f"{SERVER_URL}/realms/{REALM_NAME}/protocol/openid-connect/auth?client_id={CLIENT_ID}&redirect_uri=http://localhost:3000/callback&response_type=code&scope=openid"

    return {"auth_url": auth_url}

@app.post("/logout")
async def logout():
    try:
        data = await request.get_json()
        token = data.get("token_refresh")
        await keycloak_openid.logout(token)
        return {"status": "ok"}
    except Exception as e:
        print(f"Hiba a logout során: {e}")
        return {"error": "Internal Server Error"}, 500

@app.post("/create_room")
async def create_room():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Authorization header missing or malformed."}, 403

    token = auth_header.split(" ")[1]
    try:
        user = await check_user_loggedin(token)
        if user is None:
            return {"error": "You need to be logged in to create a room."}, 403

        if len(rooms) >= ROOM_LIMIT:
            return {"error": "Room limit reached."}, 403

        room_id = generate_room_id()
        gamestate = await generate_gamestate()
        rooms[room_id]["gamestate"] = gamestate
        await app.pool.execute(
            "INSERT INTO rooms (room_id, gamestate) VALUES ($1, $2)",
            room_id, json.dumps(gamestate)
        )
        print(f"Szoba létrehozva: {room_id}")  # Debug
        return {"room_id": room_id}
    except Exception as e:
        print(f"Hiba a create_room során: {e}")
        return {"error": "Internal Server Error"}, 500

@app.get("/rooms")
async def fetch_rooms():
    try:
        return {"rooms": list(rooms.keys())}
    except Exception as e:
        print(f"Hiba a fetch_rooms során: {e}")
        return {"error": "Internal Server Error"}, 500

@app.post("/join_room")
async def join_room():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Authorization header missing or malformed."}, 403

    token = auth_header.split(" ")[1]
    try:
        user = await check_user_loggedin(token)
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
        player_obj = {
            "name": user["preferred_username"],
            "hand": [],
            "stack": [],
            "score": 0,
            "id": user["sub"]
        }
        gamestate["players"].append(player_obj)
        rooms[room_id]["gamestate"] = gamestate
        await app.pool.execute(
            "UPDATE rooms SET gamestate = $1 WHERE room_id = $2",
            json.dumps(gamestate), room_id
        )
        print(f"Felhasználó csatlakozott: {user['preferred_username']} a szobához: {room_id}")  # Debug
        # Gamestate küldése minden kliensnek a csatlakozás után
        await broadcast(room_id, {
            "action": "gamestate",
            "gamestate": rooms[room_id]['gamestate']
        })
        return {"status": "ok", "room_id": room_id}
    except Exception as e:
        print(f"Hiba a join_room során: {e}")
        return {"error": "Internal Server Error"}, 500

@app.websocket('/ws')
async def ws():
    room_id = None
    user_id = None
    try:
        # Első üzenetnek csatlakozási kérést várunk
        data = await websocket.receive()
        print(f"Bejövő üzenet: {data}")  # Debug
        message = json.loads(data)
        
        if message['action'] == 'join':
            room_id = message['room_id']
            user_id = message['user_id']
            print(f"Csatlakozás szobához: {room_id} felhasználóval: {user_id}")  # Debug
            if room_id not in rooms:
                await websocket.send(json.dumps({"error": "Room not found."}))
                print(f"Szoba nem található: {room_id}")  # Debug
                return
            rooms[room_id]['clients'].add(websocket)
            print(f"Kliensek száma a szobában {room_id}: {len(rooms[room_id]['clients'])}")  # Debug
            
            # Jelenlegi gamestate küldése az új kliensnek
            await websocket.send(json.dumps({
                "action": "gamestate",
                "gamestate": rooms[room_id]['gamestate']
            }))
            
            # Gamestate broadcast a többi játékosnak
            await broadcast(room_id, {
                "action": "gamestate",
                "gamestate": rooms[room_id]['gamestate']
            })
        
        while True:
            data = await websocket.receive()
            print(f"Bejövő üzenet: {data}")  # Debug
            message = json.loads(data)
            
            if message['action'] == 'draw_card':
                if not rooms[room_id]['gamestate']['card_pool']:
                    await websocket.send(json.dumps({"error": "Nincs több lap a pakliban."}))
                    print("Nincs több lap a pakliban.")  # Debug
                    continue
                card = rooms[room_id]['gamestate']['card_pool'].pop()
                rooms[room_id]['gamestate']['cards'].append(card)
                print(f"Húzott lap: {card}")  # Debug
                
                # Adatbázis frissítése
                await app.pool.execute(
                    "UPDATE rooms SET gamestate = $1 WHERE room_id = $2",
                    json.dumps(rooms[room_id]['gamestate']), room_id
                )
                
                # Gamestate küldése minden kliensnek
                await broadcast(room_id, {
                    "action": "gamestate",
                    "gamestate": rooms[room_id]['gamestate']
                })
                
    except Exception as e:
        print(f"Hiba a WebSocket kapcsolatban: {e}")
    finally:
        if room_id and websocket in rooms[room_id]['clients']:
            rooms[room_id]['clients'].remove(websocket)
            if user_id:
                rooms[room_id]['gamestate']['players'] = [
                    player for player in rooms[room_id]['gamestate']['players']
                    if player['id'] != user_id
                ]
                # Adatbázis frissítése
                await app.pool.execute(
                    "UPDATE rooms SET gamestate = $1 WHERE room_id = $2",
                    json.dumps(rooms[room_id]['gamestate']), room_id
                )
                # Gamestate küldése minden kliensnek
                await broadcast(room_id, {
                    "action": "gamestate",
                    "gamestate": rooms[room_id]['gamestate']
                })
                print(f"Kilépett a szobából: {room_id} felhasználóval: {user_id}")  # Debug

async def broadcast(room_id, message):
    if room_id in rooms:
        for client in list(rooms[room_id]['clients']):
            try:
                await client.send(json.dumps(message))
            except Exception as e:
                print(f"Hiba az üzenet küldésekor a kliensnek: {e}")
                rooms[room_id]['clients'].remove(client)

def run() -> None:
    app.run()

if __name__ == "__main__":
    run()