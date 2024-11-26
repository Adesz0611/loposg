<template>
    <div>
        <div class="background">
            <header>
                <h1>Room ID: {{ room_id_store.room_id }}</h1>
            </header>
            <div class="table">
                <div class="player" id="player1">Player 1</div>
                <div class="player" id="player2">Player 2</div>
                <div class="player" id="player3">Player 3</div>
                <div class="player" id="player4">Player 4</div>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref } from 'vue';
import { useRoomIdStore } from '../stores/room_id';
import { createRouter, useRouter } from 'vue-router';
const router = useRouter();

const roomId = ref('');
const room_id_store = useRoomIdStore();


// if (!room_id_store.room_id) {
//     router.push({ name: 'home' });
// }

</script>

<style scoped>
.background {
    background-image: url('https://images.pexels.com/photos/326333/pexels-photo-326333.jpeg');
    background-size: cover;
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.table {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    width: 100%;
    padding: 1rem;
}

.player {
    background-color: #ffffff;
    border: 1px solid #000000;
    padding: 1rem;
    margin: 0.5rem 0;
    width: 100%;
    text-align: center;
}
</style>