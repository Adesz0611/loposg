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
                           client_secret_key="HAJQtPl0W5OOjxoSjXuqvgF1xyXOdDwD", # Rablo: HAJQtPl0W5OOjxoSjXuqvgF1xyXOdDwD 
                                                                                 # Adri: Xtx2kEevrqiztUZt1puOZuSmP1Zht1sq
)
keycloak_admin = kc.KeycloakAdmin(server_url="http://localhost:8080/",
                                    username="admin",
                                    password="admin",
                                    realm_name="master",
                                    verify=True,
                                    auto_refresh_token=["get", "post", "put", "delete"])


async def check_user_loggedin(token):
    try:
        user = await openid.userinfo(token)
        return user
    except kc.KeycloakAuthenticationError:
        return None
    
def generate_gamestate():
    template = {
        "card_pool": ['HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK',
                      'DA', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'DJ', 'DQ', 'DK',
                      'CA', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'CJ', 'CQ', 'CK',
                      'SA', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10', 'SJ', 'SQ', 'SK',],
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
# megszámolja, hogy a stack tetején hány egyforma kártya van
# például ['HA', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'HJ', 'HQ', 'HK', 'QK'] -> 2
def count_trailing_occurrences(lst):
    if len(lst) < 2:
        return 0
    last_card = lst[-1][1]
    count = 0
    for card in reversed(lst):
        if card[1] == last_card:
            count += 1
        else:
            break
    return count

def score_for_a_card(card):
    if card[1] in "234567":
        return 5
    else:
        return 10

def score_for_a_stack(stack):
    return sum(score_for_a_card(card) for card in stack)

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
    
    return {"user_info": user_info, "token": token, "username": user_info["preferred_username"]}

@app.post("/logout")
async def logout():
    data = await request.get_json()
    token = data.get("token_refresh")
    await openid.logout(token)
    #TODO: redirect to the main page
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

@app.get("/rooms")
async def fetch_rooms():
    room_ids = await app.pool.fetch("SELECT room_id FROM rooms")
    room_ids = [str(x["room_id"]) for x in room_ids]
    return {"rooms": room_ids}

@app.post("/profile")
async def edit_profile():
    user = await check_user_loggedin(request.headers.get("Authorization"))
    if user is None:
        return {"error": "You need to be logged in to edit your profile."}, 403

    data = await request.get_json()
    new_username = data.get("username")
    if new_username:
        await keycloak_admin.update_user(user["sub"], {"username": new_username})
    new_password = data.get("password")
    if new_password:
        await keycloak_admin.set_user_password(user["sub"], new_password, temporary=False)
    return {"status": "ok"}

@app.get("/leaderboard")
async def leaderboard():
    leaderboard_db = await app.pool.fetch("SELECT * FROM leaderboard ORDER BY score DESC")
    # leaderboard = [{"user_id": x["user_id"], "score": x["score"]} for x in leaderboard]
    leaderboard = []
    for x in leaderboard_db:
        user = await keycloak_admin.get_user(x["user_id"])
        ret = {"user_id": x["user_id"], "score": x["score"]}
        ret["username"] = user["username"]
        leaderboard.append(ret)
    return {"leaderboard": leaderboard}

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
    await sio.emit("player_joined", {"player_name": username, "player_count" : len(gamestate["players"])}, room=room_id)

    # send the other players the new player order
    player_order_names = [gamestate["players"][player_id]["name"] for player_id in gamestate["player_order"]]
    await sio.emit("player_order", {"player_order": player_order_names}, room=room_id)

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
    
    # draw one card for the main discard pile
    gamestate["cards"] = gamestate["card_pool"][:1]
    gamestate["card_pool"] = gamestate["card_pool"][1:]

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
        "current_player": gamestate["players"][gamestate["player_order"][gamestate["current_player"]]]["name"],
        "main_stack": gamestate["cards"],
        "started": gamestate["started"],
        "player_order": gamestate["player_order"],
        "card_pool": gamestate["card_pool"],
        "current_player": gamestate["players"][gamestate["player_order"][gamestate["current_player"]]]["name"],
    }

    #global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-2:] for player_id in gamestate["player_order"]]
    #global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]]
    global_gamestate["player_stack"] = {gamestate["players"][player_id]["name"]: gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]}    
    global_gamestate["players_hand"] = {gamestate["players"][player_id]["name"]: len(gamestate["players"][player_id]["hand"]) for player_id in gamestate["player_order"]}
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

    if action == "discard":
        await action_discard(sid, data, gamestate, user_id, room_id)
    elif action == "pair":
        await action_pair(sid, data, gamestate, user_id, room_id)
    elif action == "steal":
        await action_steal(sid, data, gamestate, user_id, room_id)

async def action_discard(sid, data, gamestate, user_id, room_id):
    if "card" not in data:
        await sio.emit("error", {"msg": "Card is required."}, to=sid)
        return

    card = data["card"]
    if card not in gamestate["players"][user_id]["hand"]:
        await sio.emit("error", {"msg": "You don't have this card."}, to=sid)
        return

    gamestate["players"][user_id]["hand"].remove(card)
    gamestate["cards"].append(card)

    # check if every player has 0 cards in their hands
    if all(len(gamestate["players"][player_id]["hand"]) == 0 for player_id in gamestate["player_order"]):
        # deal max 5 cards to each player if there are smaller than 5 times number of players in the card pool deal the remaining cards equally if cannot deal equally the remaining cards then print game over
        if len(gamestate["card_pool"]) < 5 * len(gamestate["player_order"]):
            num_of_cards = len(gamestate["card_pool"]) // len(gamestate["player_order"])
        else:
            num_of_cards = 5
        
        if (num_of_cards == 0):
            # calculate the scores
            for player_id in gamestate["players"]:
                gamestate["players"][player_id]["score"] = score_for_a_stack(gamestate["players"][player_id]["stack"])

            await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

            # calculate the winner
            max_score = gamestate["players"][max(gamestate["players"], key=lambda x: gamestate["players"][x]["score"])]["score"]
            #get the id of the max score
            winner_id = [key for key in gamestate["players"] if gamestate["players"][key]["score"] == max_score][0]
            winner_username = gamestate["players"][winner_id]["name"]
            row = await app.pool.fetchrow("SELECT * FROM leaderboard WHERE user_id = $1", (winner_id))
            if not row:
                await app.pool.execute("INSERT INTO leaderboard (user_id, score) VALUES ($1, $2)", (winner_id), max_score)
            else:
                await app.pool.execute("UPDATE leaderboard SET score = $1 WHERE user_id = $2", max_score, (winner_id))
                
            await sio.emit("game_over", {"msg": "No more cards in the card pool.", "winner": winner_username, "winner_score": max_score}, room=room_id)
            # send the store to the players
            for player_id in gamestate["players"]:
                await sio.emit("own_gamestate", gamestate["players"][player_id], to=user_id2sid[player_id])
            return

        for player_id in gamestate["players"]:
            gamestate["players"][player_id]["hand"] = gamestate["card_pool"][:num_of_cards]
            gamestate["card_pool"] = gamestate["card_pool"][num_of_cards:]

    curr_player = (gamestate["current_player"] + 1) % len(gamestate["player_order"])
    while len(gamestate["players"][gamestate["player_order"][curr_player]]["hand"]) == 0:
        curr_player = (curr_player + 1) % len(gamestate["player_order"])
    gamestate["current_player"] = curr_player

    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    global_gamestate = {
        "current_player": gamestate["players"][gamestate["player_order"][gamestate["current_player"]]]["name"],
        "main_stack": gamestate["cards"],
        "started": gamestate["started"],
        "player_order": gamestate["player_order"],
        "card_pool": gamestate["card_pool"],
    }
    #global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-2:] for player_id in gamestate["player_order"]]
    #global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]]
    global_gamestate["player_stack"] = {gamestate["players"][player_id]["name"]: gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]}    
    global_gamestate["players_hand"] = {gamestate["players"][player_id]["name"]: len(gamestate["players"][player_id]["hand"]) for player_id in gamestate["player_order"]}
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

    if card1[1] != card2[1]:  # Assuming card format is like 'HA', 'H2', etc.
        await sio.emit("error", {"msg": "Cards are not a pair."}, to=sid)
        return

    gamestate["players"][user_id]["hand"].remove(card1)
    gamestate["players"][user_id]["hand"].remove(card2)
    gamestate["players"][user_id]["stack"].extend([card1, card2])

    # check if every player has 0 cards in their hands
    if all(len(gamestate["players"][player_id]["hand"]) == 0 for player_id in gamestate["player_order"]):
        # deal max 5 cards to each player if there are smaller than 5 times number of players in the card pool deal the remaining cards equally if cannot deal equally the remaining cards then print game over
        if len(gamestate["card_pool"]) < 5 * len(gamestate["player_order"]):
            num_of_cards = len(gamestate["card_pool"]) // len(gamestate["player_order"])
        else:
            num_of_cards = 5
        
        if (num_of_cards == 0):
            # calculate the scores
            for player_id in gamestate["players"]:
                gamestate["players"][player_id]["score"] = score_for_a_stack(gamestate["players"][player_id]["stack"])

            await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

            # calculate the winner
            winner = max(gamestate["players"], key=lambda x: gamestate["players"][x]["score"])
            score = winner["score"]
            winner_username = winner["name"]
            
            await sio.emit("game_over", {"msg": "No more cards in the card pool.", "winner": winner_username, "winner_score": score}, room=room_id)
            # send the store to the players
            for player_id in gamestate["players"]:
                await sio.emit("own_gamestate", gamestate["players"][player_id], to=user_id2sid[player_id])
            return

        for player_id in gamestate["players"]:
            gamestate["players"][player_id]["hand"] = gamestate["card_pool"][:num_of_cards]
            gamestate["card_pool"] = gamestate["card_pool"][num_of_cards:]

    curr_player = (gamestate["current_player"] + 1) % len(gamestate["player_order"])
    while len(gamestate["players"][gamestate["player_order"][curr_player]]["hand"]) == 0:
        curr_player = (curr_player + 1) % len(gamestate["player_order"])
    gamestate["current_player"] = curr_player

    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    global_gamestate = {
        "current_player": gamestate["players"][gamestate["player_order"][gamestate["current_player"]]]["name"],
        "main_stack": gamestate["cards"],
        "started": gamestate["started"],
        "player_order": gamestate["player_order"],
        "card_pool": gamestate["card_pool"],
    }
    #global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-2:] for player_id in gamestate["player_order"]]
    # global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]]
    global_gamestate["player_stack"] = {gamestate["players"][player_id]["name"]: gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]}
    global_gamestate["players_hand"] = {gamestate["players"][player_id]["name"]: len(gamestate["players"][player_id]["hand"]) for player_id in gamestate["player_order"]}
    await sio.emit("global_gamestate", global_gamestate, room=room_id)

    for player_id in gamestate["players"]:
        await sio.emit("own_gamestate", gamestate["players"][player_id], to=user_id2sid[player_id])

async def action_steal(sid, data, gamestate, user_id, room_id):
    if "card" not in data:
        await sio.emit("error", {"msg": "Card is required."}, to=sid)
        return
    
    if "target" not in data:
        await sio.emit("error", {"msg": "Target is required."}, to=sid)
        return

    card = data["card"]
    target = data["target"]

    # get the user_id from the username
    target = [player_id for player_id in gamestate["players"] if gamestate["players"][player_id]["name"] == target]
    if len(target) != 1:
        await sio.emit("error", {"msg": "Target not found."}, to=sid)
        return
    target = target[0]


    #TODO: do it for all the similar cards

    # for i in range(count_trailing_occurrences(gamestate["players"][target]["stack"])):
    #     reversed(gamestate["players"][target]["stack"]).pop(0)

    if card[1] != gamestate["players"][target]["stack"][-1][1]:
        await sio.emit("error", {"msg": "You cannot steal this card."}, to=sid)
        return
    
    howmany = count_trailing_occurrences(gamestate["players"][target]["stack"])
    gamestate["players"][user_id]["stack"].extend(gamestate["players"][target]["stack"][-howmany:])
    gamestate["players"][target]["stack"] = gamestate["players"][target]["stack"][:-howmany]

    gamestate["players"][user_id]["hand"].remove(card)
    gamestate["players"][user_id]["stack"].append(card)

    await app.pool.execute("UPDATE rooms SET gamestate = $1 WHERE room_id = $2", json.dumps(gamestate), int(room_id))

    global_gamestate = {
        "current_player": gamestate["players"][gamestate["player_order"][gamestate["current_player"]]]["name"],
        "main_stack": gamestate["cards"],
        "started": gamestate["started"],
        "player_order": gamestate["player_order"],
        "card_pool": gamestate["card_pool"],
    }
    # global_gamestate["players_stack"] = [gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]]
    global_gamestate["player_stack"] = {gamestate["players"][player_id]["name"]: gamestate["players"][player_id]["stack"][-count_trailing_occurrences(gamestate["players"][player_id]["stack"]):] for player_id in gamestate["player_order"]}
    global_gamestate["players_hand"] = {gamestate["players"][player_id]["name"]: len(gamestate["players"][player_id]["hand"]) for player_id in gamestate["player_order"]}
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
