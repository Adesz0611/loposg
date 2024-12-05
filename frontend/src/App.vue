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
        <BDropdownItem @click="showModal = true">Kijelentkezés</BDropdownItem>
      </BNavItemDropdown>
    </BNavbarNav>
  </BNavbar>
  <div style="padding-top: 56px; padding-bottom: 56px;">
    <BModal v-model="showModal" title="Kijelentkezés" @ok="logout" @cancel="showModal = false" ok-title="Kilépés"
      cancel-title="Vissza">
      Biztosan ki szeretnél jelentkezni?
    </BModal>
    <RouterView />
  </div>
  <footer>
    <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcREkQLaAXGL_L52wymdCdAp3Ep-3O6JzBp_Wg&s" />
    <p style="text-align: right; color: white">&copy;LopósG kártyajáték</p>
  </footer>
</template>

<script setup>
import { RouterView } from 'vue-router';
import { useUsernameStore } from './stores/username.js';
import { onBeforeMount, ref } from 'vue';
import axios from 'axios';
import router from './router/index.js';
import { BModal } from 'bootstrap-vue-next';

onBeforeMount(() => {
  if (localStorage.getItem('access_token')) {
    console.log('access token found');
    console.log('username: ' + localStorage.getItem('username'));
    username_store.username = localStorage.getItem('username');
    // TODO: get username from keycloak
  }
});
const showModal = ref(false);
const username_store = useUsernameStore();
function logout() {
  axios.post('http://localhost:5000/logout', {
    token_refresh: localStorage.getItem('refresh_token'),
  },
  ).then(response => {
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
