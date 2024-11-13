// FILE: src/main.js

import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue' 
import router from './router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { useWebSocketStore } from './stores/websocket'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

// Inicializáljuk a WebSocket-t
const wsStore = useWebSocketStore()
wsStore.initWebSocket()

app.mount('#app')