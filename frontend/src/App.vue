<template>
  <button @click="login">Login</button>
  <button @click="logout">Logout</button>
  <button @click="create_room">Szoba létrehozása</button>
  <button @click="get_card">Lap húzás</button>
  <p>Card: {{ card }}</p>
  <p>Room id: {{ room_id }}</p>
  <!-- <RouterView />-->
</template>

<script setup>
//import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue';
import axios from 'axios';

const room_id = ref('');
const card = ref('');

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

function logout() {
  axios.post('http://localhost:5000/logout', {
    token_refresh: localStorage.getItem('refresh_token'),
  }, )
    .then(response => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      alert('Kijelentkeztél!');
    })
    .catch((error) => {
      console.log(error)
    });
}

const cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

function get_card() {
  card.value = cards[Math.floor(Math.random() * cards.length)];
}
</script>


<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
