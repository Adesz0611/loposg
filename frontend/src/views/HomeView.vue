<template>
  <button @click="login">Login</button>
  <button @click="logout">Logout</button>
  <button @click="create_room">Szoba létrehozása</button>
  <button @click="get_card">Lap húzás</button>
  <textarea v-model="join_text" placeholder="Szoba azonosító"></textarea>
  <button @click="join_room">Csatlakozás a szobához</button>
  <p>Card: {{ card }}</p>
  <p>Room id: {{ room_id }}</p>
  <button @click="fetch_rooms">Szobák lekérése</button>
  faszfasz {{ room_id_store.room_id }}
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue';
import { createRouter, useRouter } from 'vue-router';
import axios from 'axios';
import { useRoomIdStore } from '../stores/room_id';

const room_id = ref('');
const card = ref('');
const join_text = ref('');

const room_id_store = useRoomIdStore();

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
      alert('Kijelentkeztél! Viszlát user: ' + response.data.username);
    })
    .catch((error) => {
      console.log(error)
    });
}

function create_room() {
  axios.post('http://localhost:5000/create_room', {}, {
    headers: {
      'Authorization': localStorage.getItem('access_token')
    }
  }).then(response => {
    room_id.value = response.data.room_id;
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
  axios.post('http://localhost:5000/join_room', {
    room_id: join_text.value
  }, {
    headers: {
      'Authorization': localStorage.getItem('access_token')
    }
  }).then(response => {
    room_id_store.room_id = response.data.room_id;
    router.push({ path: '/play' });
    console.log(response.data);
  })
}
const cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

function get_card() {
  card.value = cards[Math.floor(Math.random() * cards.length)];
}
</script>
