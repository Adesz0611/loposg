<template>
  <!-- background image -->
  <div class="bg-image"></div>
  <BListGroup class="mt-auto">
    <BListGroupItem>
      <BButton variant="success" @click="login" style="width: 100%;">Bejelentkezés/Regisztráció</BButton>
    </BListGroupItem>
    <BListGroupItem>
      <BButton @click="create_room" variant="warning" style="width: 100%;">Szoba létrehozása</BButton>
    </BListGroupItem>
    <BListGroupItem>
      <BInputGroup prepend="Szoba azonosító">
        <BFormInput v-model="join_text" />
        <BButton @click="join_room" variant="info">Csatlakozás</BButton>
      </BInputGroup>
    </BListGroupItem>
  </BListGroup>
</template>


<script setup>
import { ref } from 'vue';
import { createRouter, useRouter } from 'vue-router';
import axios from 'axios';
import { useRoomIdStore } from '../stores/room_id';
import { useUsernameStore } from '../stores/username';
import { BInputGroup, BFormInput, BButton, BContainer, BRow, BCol } from 'bootstrap-vue-next';
const join_text = ref('');
const room_id_store = useRoomIdStore();
const username_store = useUsernameStore();

function login() {
  axios.get('http://localhost:5000/login')
    .then(response => {
      window.location.href = response.data.auth_url;
    })
    .catch((error) => {
      console.log(error)
    });
}

function logout() {
  axios.post('http://localhost:5000/logout', {
    token_refresh: localStorage.getItem('refresh_token'),
  },)
    .then(response => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      alert('Kijelentkeztél! Viszlát user: ' + username_store.username);
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
    router.push({ path: '/play' });
    room_id_store.room_id = response.data.room_id;
  })
    .catch((error) => {
      console.log(error)
    });
}

function fetch_rooms() {
  axios.get('http://localhost:5000/rooms', {
    headers: {
      'Authorization': localStorage.getItem('access_token')
    }
  }).then(response => {
    console.log(response.data);
  })
    .catch((error) => {
      console.log(error)
    });
}

const router = useRouter();
function join_room() {
  axios.post('http://localhost:5000/rooms/' + join_text.value + '/join', {
  }, {
    headers: {
      'Authorization': localStorage.getItem('access_token')
    }
  }).then(response => {
    room_id_store.room_id = response.data.room_id;
    router.push({ path: '/play' });
  })
}
</script>

<style scoped>
.mt-auto {
  /* center */
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-top: auto;
  margin-left: auto;
}

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