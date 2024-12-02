<template>
    <div>
        <div class="bg-image"></div> <!-- Background image -->
        <div class="container"> <!-- Container for form -->
            <header>
                <!-- <BThead style="color: blue;">Profil</BThead> -->
                <h1 class="text-oldalcim">Profil</h1>
            </header>

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
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoomIdStore } from '../stores/room_id';
import { createRouter, useRouter } from 'vue-router';

const router = useRouter();
const roomIdStore = useRoomIdStore();
const userName = ref('John Doe');
const userPassword = ref('');

// Function to handle profile update
function updateProfile() {
    // Placeholder for the update functionality
    console.log(`UserName: ${userName.value}, Password: ${userPassword.value}`);
}

function goToHome() {
    router.push('/');
}
</script>

<style scoped>
.bg-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('https://images.unsplash.com/photo-1646809014367-2c267bcba69f?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
    background-size: cover;
    background-position: center;
    z-index: -1;
}

body {
    background-color: transparent;
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.container {
    background-color: #ffffff;
    padding: 2rem;
    margin: 2rem auto;
    width: 90%;
    max-width: 800px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}

header {
    background-color: #4CAF50;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
    border-radius: 8px 8px 0 0;
}

.text-oldalcim {
    color: #ffffff;
    font-size: 24px;
    font-weight: bold;
    margin: 0;
}

form div {
    margin-bottom: 1rem;
}

input[type="text"], input[type="password"] {
    width: 100%;
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 0.5rem;
}

button {
    background-color: #4CAF50;
    color: white;
    padding: 0.8rem 1.5rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    width: 100%;
    margin-top: 1rem;
}

button:hover {
    background-color: #45a049;
}
</style>
