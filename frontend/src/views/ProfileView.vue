<template>
    <div>
        <header>
            <!-- <BThead style="color: blue;">Profil</BThead> -->
        </header>
    </div>
    <div>
        <form @submit.prevent="updateProfile">
            <div>
                <label for="username">felhasználónév:</label>
                <input id="username" v-model="userName" type="text" />
            </div>
            <div>
                <label for="password">Jelszó:</label>
                <input id="password" v-model="userPassword" type="password" />
            </div>
            <button type="submit">Adatok frissítése</button>
        </form>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoomIdStore } from '../stores/room_id';
import { createRouter, useRouter } from 'vue-router';
const router = useRouter();

const roomIdStore = useRoomIdStore();
const userName = ref('John Doe');
const userEmail = ref('john.doe@example.com');

function goToHome() {
    router.push('/');
}

</script>

<style scoped>
header {
    background-color: #f8f9fa;
    padding: 1rem;
    text-align: center;
}

h1 {
    margin: 0;
    font-size: 1.5rem;
}
</style>