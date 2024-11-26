import { reactive } from 'vue';
import { connect, io } from 'socket.io-client';

export const state = reactive({
    connected: false,
});

const URL = 'http://localhost:5000';

export const socket = io(URL);

socket.on('connect', () => {
    state.connected = true;
});

socket.on('disconnect', () => {
    state.connected = false;
});