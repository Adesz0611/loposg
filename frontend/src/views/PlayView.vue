<template>
    <div class="background">
        <div class="teteje w-100"></div>
        <div class="kozepe w-100">
            <div class="asztal">
                <p id="room-id">{{ props.room_id }}</p>
                <button class="btn btn-primary d-block mt-5 mx-auto" @click="start_game">Játék indítása</button>
            </div>
            <div class="asztal">
                <p id="room-id">{{ props.room_id }}</p>
                <button class="btn btn-primary d-block mt-5 mx-auto" @click="start_game">Játék indítása</button>
            </div>
            <div class="asztal">
                <p id="room-id">{{ props.room_id }}</p>
                <button class="btn btn-primary d-block mt-5 mx-auto" @click="start_game">Játék indítása</button>
            </div>
        </div>
        <div class="alja w-100"></div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({ room_id: String });

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
    justify-content: center;
    align-items: center;
}

#room-id {
    text-align: center;
    font-size: 2rem;
}

.teteje {
    display: flex;
    justify-content: space-between;
}

.alja {
    display: flex;
    justify-content: space-between;
}

.kozepe {
    display: flex;
    justify-content: space-between;
    gap: 20px;
}

.asztal {
    display: flex;
    flex-direction: column;
    background-color: #C19A6B;
    height: 200px;
    width: 40%;
    padding: 1rem;
    border-radius: 1rem;
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