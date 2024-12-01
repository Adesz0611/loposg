import { reactive } from 'vue';
import { io } from 'socket.io-client';

export const state = reactive({
    connected: false,
});

const URL = 'http://localhost:5000';

export const socket = io(URL);

socket.on('connect', () => {
    state.connected = true;
    console.log('Connected:', state.connected);
});

socket.on('disconnect', () => {
    state.connected = false;
    console.log('Disconnected:', state.connected);
});