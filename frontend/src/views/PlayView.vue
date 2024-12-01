<template>
    <div class="background">
        <div class="teteje w-100">
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="playing-cards-assets/png/back.png" :show="true" :number="5" />
                    <Card path="playing-cards-assets/png/CQ.png" />
                </div>
            </div>
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="playing-cards-assets/png/back.png" :show="true" :number="5" />
                    <Card path="playing-cards-assets/png/CQ.png" />
                </div>
            </div>
        </div>
        <div class="kozepe w-100">
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="playing-cards-assets/png/back.png" :show="true" :number="5" />
                    <Card path="playing-cards-assets/png/CQ.png" />
                </div>
            </div>
            <div class="asztal">
                <p id="room-id">{{ props.room_id }}</p>
                <button class="btn btn-primary d-block mt-5 mx-auto" @click="start_game">Játék indítása</button>
            </div>
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="playing-cards-assets/png/back.png" :show="true" :number="5" />
                    <Card path="playing-cards-assets/png/CQ.png" />
                </div>
            </div>
        </div>
        <div class="alja w-100">
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="playing-cards-assets/png/back.png" :show="true" :number="5" />
                    <Card path="playing-cards-assets/png/CQ.png" />
                </div>
            </div>
            <div class="player">
                <p id="username">Játékosnév</p>
                <div class="hand">
                    <Card path="playing-cards-assets/png/back.png" :show="true" :number="5" />
                    <Card path="playing-cards-assets/png/CQ.png" />
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Card from '../components/Card.vue';

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
    flex-direction: column;
    justify-content: center;
    /* align-items: center; */
    padding: 1%;
}

#username {
    text-align: center;
    font-size: 1rem;
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
    justify-content: space-between;
    gap: 20%;
}

.alja {
    display: flex;
    justify-content: space-between;
    gap: 20%;
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

.player {
    display: flex;
    flex-direction: column;
    background-color: #ffffff;
    border: 1px solid #000000;
    padding: 1rem;
    margin: 0.5rem 0;
    width: 100%;
    text-align: center;
}

.hand {
    display: flex;
    justify-content: center;
    gap: 1%;
}

.stack {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 1rem;
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