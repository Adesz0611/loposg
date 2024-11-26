import './assets/main.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue' 
import router from './router'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import {createBootstrap} from 'bootstrap-vue-next'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.use(createBootstrap()) 

app.mount('#app')
