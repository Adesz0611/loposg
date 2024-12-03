<template>
    <div class="background">
        <div class="teteje w-100">
            <div class="player" :class="{ current_player: players[1] == current_player }" v-show="player_count > 2">
                <p id="username">{{ players[1] }}</p>
                <div class="hand">
                    <Card :path="(true) ? 'png/empty.png' : ('png/' + player_stack[1][0] + '.png')" :show="false"
                        style="transform: scale(1.2);" />
                    <Card path="png/CQ.png" :show="true" :number="2" />
                </div>
            </div>
            <div class="player" :class="{ current_player: players[3] == current_player }" v-show="player_count > 4">
                <p id="username">{{ players[3] }}</p>
                <div class="hand">
                    <Card path="png/CQ.png" :show="true" :number="5" />
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                </div>
            </div>
        </div>
        <div class="kozepe w-100">
            <div class="player" :class="{ current_player: players[0] == current_player }" v-show="player_count > 1">
                <p id="username">{{ players[0] }}</p>
                <div class="hand">
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                    <Card path="png/HJ.png" :show="true" :number="3" />
                </div>
            </div>
            <div class="asztal">
                <div v-show="!game_started">
                    <p id="room-id">A szoba azonosítója:</p>
                    <p id="room-id">{{ props.room_id }}</p>
                    <button class="btn btn-primary d-block mx-auto" @click="start_game">Játék indítása</button>
                </div>
                <div v-show="game_started" class="midgame">
                    <Card path="png/back.png" :show="true" :number="remaining_card_count" style="scale: 1.1;" />
                    <Card
                        :path="main_stack[main_stack.length - 1] ? 'png/' + main_stack[main_stack.length - 1] + '.png' : 'png/empty.png'"
                        :show="false" />
                </div>
            </div>
            <div class="player" :class="{ current_player: players[2] == current_player }" v-show="player_count > 3">
                <p id="username">{{ players[2] }}</p>
                <div class="hand">
                    <Card path="png/CQ.png" :show="true" :number="5" />
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                </div>
            </div>
        </div>
        <div class="alja w-100">
            <div class="player" :class="{ current_player: username_store.username == current_player }">
                <p id="username">{{ username_store.username }} (én)</p>
                <div class="player_hand">
                    <Card :path="'png/' + my_stack[my_stack.length - 1] + '.png'" :show="false"
                        style="transform: scale(1.2);" />
                    <div class="hand">
                        <Card v-for="card in my_cards" :key="card" :path="'png/' + card + '.png'"
                            @click="selected_card = card" :selected="card == selected_card" />
                    </div>
                    <BButtonGroup>
                        <BButton pill variant="primary" @click="discard">Kártya eldobása</BButton>
                        <BButton pill variant="success" @click="pair">Kártya lerakása</BButton>
                        <BButton pill variant="danger" @click="steal">Lopás</BButton>
                    </BButtonGroup>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onBeforeMount, computed } from 'vue';
import { socket } from '../socket';
import Card from '../components/Card.vue';
import { useUsernameStore } from '@/stores/username';

const props = defineProps({ room_id: String });
const username_store = useUsernameStore();


onBeforeMount(() => {
    socket.emit('join_room', { room_id: props.room_id, bearer: localStorage.getItem('access_token') });
    socket.on('error', (data) => {
        alert("Figyelj öcsi, baj van: " + data.msg);
    });
    // socket.on('player_joined', (data) => {
    //     console.log("Játékos csatlakozott: " + data.player_name);
    //     players.value.push(data.player_name);
    //     player_count.value = data.player_count;
    // });
    socket.on('player_order', (data) => {
        console.log("Játékos sorrend: ", data.player_order);
        const filtered = data.player_order.filter(player => player != username_store.username);
        players.value = filtered;
    });
    socket.on('own_gamestate', (data) => {
        my_cards.value = data.hand;
        my_stack.value = data.stack;
        console.log('o gamestate: ', data);
    });
    socket.on('global_gamestate', (data) => {
        game_started.value = data.started;
        main_stack.value = data.main_stack;
        remaining_card_count.value = data.card_pool.length;
        current_player.value = data.current_player;
        player_stack.value = data.player_stack;
        console.log('g gamestate: ', data);
    });

});

const players = ref([]);
const player_count = computed(() => players.value.length + 1);
const current_player = ref('');
const main_stack = ref([]);
const game_started = ref(false);
const my_cards = ref([]);
const selected_card = ref('');
const my_stack = ref(['empty']);
const player_stack = ref([['empty'], ['empty'], ['empty'], ['empty']]);
const remaining_card_count = ref(0);

function start_game() {
    console.log('starting game...');
    socket.emit('start_game', { room_id: props.room_id });
}
function discard() {
    socket.emit('card_action', { room_id: props.room_id, card: selected_card.value, action: 'discard' });
}

function pair() {
    let pair_card = my_cards.value.find(card => card[1] == selected_card.value[1] && card != selected_card.value);
    socket.emit('card_action', { room_id: props.room_id, cards: [selected_card.value, pair_card], action: 'pair' });
    console.log('pair');
}

function steal() {
    socket.emit('card_action', { room_id: props.room_id, card: selected_card.value, action: 'steal' });
    console.log('steal');
}

</script>

<style scoped>
.background {
    background-image: url('https://images.pexels.com/photos/326333/pexels-photo-326333.jpeg');
    background-size: cover;
    width: 100vw;
    height: calc(100vh - 112px);
    display: flex;
    flex-direction: column;
    justify-content: center;
    /* align-items: center; */
    padding: 1%;
}

#username {
    text-align: center;
    font-size: 1.5rem;
}

#room-id {
    text-align: center;
    font-size: 2rem;
}

.teteje {
    display: flex;
    justify-content: space-between;
    gap: 20%;
}

.kozepe {
    display: flex;
    /* justify-content: space-between; */
    gap: 4%;
}

.alja {
    display: flex;
    justify-content: center;
    gap: 20%;
}

.asztal {
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 1rem;
    background-color: #C19A6B;
    height: 200px;
    width: 100%;
    padding: 1rem;
    border-radius: 1rem;
}

.midgame {
    display: flex;
    justify-content: center;
    gap: 1rem;
    scale: 1.4;
}

.player {
    display: flex;
    flex-direction: column;
    background-color: rgba(255, 255, 255, 0.5);
    border-radius: 20px;
    padding: 1rem;
    margin: 0.5rem 0;
    width: 100%;
    text-align: center;
}

.current_player {
    background-color: rgba(175, 225, 175, 0.5) !important;
}

.hand {
    display: flex;
    justify-content: center;
    gap: 2%;
}

.player_hand {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 7%;
}

.stack {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 1rem;
}
</style>