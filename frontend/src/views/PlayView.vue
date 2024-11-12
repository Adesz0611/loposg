<template>
    <div>
        <header>
            <h1 style="color: blue;">Room ID: {{ room_id_store.room_id }}</h1>
        </header>
    </div>
    <p class="text-center">This is the Play view</p>
</template>

<script setup>
import { ref } from 'vue';
import { useRoomIdStore } from '../stores/room_id';

const roomId = ref('');
const room_id_store = useRoomIdStore();
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