<template>
    <div class="background">
        <div class="teteje w-100">
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                    <Card path="png/CQ.png" :show="true" :number="2" />
                </div>
            </div>
            <div class=" player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="png/CQ.png" :show="true" :number="5" />
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                </div>
            </div>
        </div>
        <div class="kozepe w-100">
            <div class="player" style="opacity: 1">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                    <Card path="png/HJ.png" :show="true" :number="3" />
                </div>
            </div>
            <div class="asztal">
                <div v-show="!game_started" class="pregame">
                    <p id="room-id">A szoba azonosítója:</p>
                    <p id="room-id">{{ props.room_id }}</p>
                    <button class="btn btn-primary d-block mx-auto" @click="start_game">Játék indítása</button>
                </div>
                <div v-show="game_started" class="midgame">
                    <Card path="png/back.png" :show="false" style="scale: 1.1;" />
                    <Card path="png/DA.png" :show="false" />
                </div>
            </div>
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="png/CQ.png" :show="true" :number="5" />
                    <Card path="png/back.png" :show="true" :number="5" style="scale: 1.1;" />
                </div>
            </div>
        </div>
        <div class="alja w-100">
            <div class="player">
                <p id="username">{{ username_store.username }} (én)</p>
                <div class="player_hand">
                    <Card path="png/SA.png" :show="true" :number="6" style="transform: scale(1.3);" />
                    <div class="hand">
                        <Card v-for="card in my_cards" :key="card" :path="'png/' + card + '.png'" />
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
import { ref, onBeforeMount } from 'vue';
import { socket } from '../socket';
import Card from '../components/Card.vue';
import { useUsernameStore } from '@/stores/username';
// import { BButton, BButtonGroup } from 'bootstrap-vue-next/dist/bootstrap-vue-next.umd';

const props = defineProps({ room_id: String });
const username_store = useUsernameStore();


onBeforeMount(() => {
    socket.emit('join_room', { room_id: props.room_id, bearer: localStorage.getItem('access_token') });
    socket.on('error', (data) => {
        alert("Figyelj öcsi, baj van: " + data.msg);
    });
    socket.on('player_joined', (data) => {
        console.log("Játékos csatlakozott: " + data.player_name);
    });
});

const game_started = ref(false);
const my_cards = ref(['C8', 'HQ', 'SA']);

function discard() {
    console.log('discard');
}

function pair() {
    console.log('pair');
}

function steal() {
    console.log('steal');
}

function start_game() {
    console.log('start game');
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
    gap: 8%;
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