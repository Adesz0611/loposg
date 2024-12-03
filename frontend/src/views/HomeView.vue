<template>
  <!-- background image -->
  <div class="container">
    <div class="bg-image"></div>
    <div class="d-flex flex-column" style="min-height: calc(100vh - 112px);">
      <BListGroup class="my-auto">
        <div v-if="!isLoggedIn">
          <BListGroupItem>
            <BButton variant="success" @click="login" style="width: 100%;">Bejelentkezés/Regisztráció</BButton>
          </BListGroupItem>
        </div>
        <div v-else>
          <BListGroupItem>
            <BButton @click="create_room" variant="warning" style="width: 100%;">Szoba létrehozása</BButton>
          </BListGroupItem>
          <BListGroupItem>
            <BInputGroup prepend="Szoba azonosító">
              <BFormInput v-model="join_text" />
              <BButton @click="join_room" variant="info">Csatlakozás</BButton>
            </BInputGroup>
          </BListGroupItem>
        </div>
      </BListGroup>
    </div>
  </div>
</template>


<script setup>
import { ref, computed } from 'vue';
import { createRouter, useRouter } from 'vue-router';
import axios from 'axios';
import { useRoomIdStore } from '../stores/room_id';
import { useUsernameStore } from '../stores/username';
import { BInputGroup, BFormInput, BButton, BContainer, BRow, BCol } from 'bootstrap-vue-next';

import { socket, state } from '../socket';

const ws_connected = computed(() => state.connected);
const isLoggedIn = computed(() => username_store.username != '');

const join_text = ref('');
const room_id_store = useRoomIdStore();
const username_store = useUsernameStore();
const router = useRouter();

function login() {
  axios.get('http://localhost:5000/login')
    .then(response => {
      window.location.href = response.data.auth_url;
    })
    .catch((error) => {
      console.log(error)
    });
}

function create_room() {
  axios.post('http://localhost:5000/rooms', {}, {
    headers: {
      'Authorization': localStorage.getItem('access_token')
    }
  }).then(response => {
    router.push({ path: '/' + response.data.room_id });
    room_id_store.room_id = response.data.room_id;
  })
    .catch((error) => {
      console.log(error)
    });
}

function join_room() {
  if (localStorage.getItem('access_token') == null) {
    alert('Nem vagy bejelentkezve!');
    return;
  }
  router.push({ path: '/' + join_text.value });

}
</script>

<style scoped>
/* .mt-auto {
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: auto;
  margin-left: auto;
} */

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
</style>