<template>
  <BNavbar v-b-color-mode="'dark'" variant="primary" class="navbar">
    <BNavbarNav>
      <BNavItem href="/">Kezdőlap</BNavItem>
      <BNavItem href="/rules">Szabályok</BNavItem>
      <BNavItem href="/leaderboard">Ranglista</BNavItem>
    </BNavbarNav>
    <BNavbarNav class="ml-auto">
      <BNavItemDropdown :text="username_store.username">
        <BDropdownItem href="/profile">Profil</BDropdownItem>
        <BDropdownItem @click="logout">Kijelentkezés</BDropdownItem>
      </BNavItemDropdown>
    </BNavbarNav>
  </BNavbar>
  <div style="padding-top: 56px; padding-bottom: 56px;">
    <RouterView />
  </div>
  <footer>
    <img src="https://vuejs.org/images/logo.png" alt="Vue.js logo" />
    <p style="text-align: right; color: white">&copy;LopósG kártyajáték</p>
  </footer>
</template>

<script setup>
import { RouterView } from 'vue-router';
import { useUsernameStore } from './stores/username.js';
import { onBeforeMount } from 'vue';
import axios from 'axios';
import router from './router/index.js';

onBeforeMount(() => {
  if (localStorage.getItem('access_token')) {
    console.log('access token found');
    console.log('username: ' + localStorage.getItem('username'));
    username_store.username = localStorage.getItem('username');
  }
});
const username_store = useUsernameStore();

function logout() {
  axios.post('http://localhost:5000/logout', {
    token_refresh: localStorage.getItem('refresh_token'),
  },
  ).then(response => {
    alert('Kijelentkeztél! Viszlát user: ' + username_store.username);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('isUserLoggedIn');
    localStorage.removeItem('username');
    username_store.username = '';
    router.push({ path: '/' });
  })
    .catch((error) => {
      console.log(error)
    });
}

</script>


<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;

  background-color: #382e88;
}

footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: #382e88;
  padding: 1rem;
  text-align: left;
}

footer p {
  margin: 0;
  position: relative;
  right: 0.5rem;
}

footer img {
  width: 50px;
  position: absolute;
  left: 0.5rem;
  bottom: 0.3rem;
}
</style>
