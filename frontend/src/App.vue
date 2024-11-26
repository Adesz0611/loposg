<template>
  <BNavbar v-b-color-mode="'dark'" variant="primary" class="navbar">
    <BNavbarNav>
      <BNavItem href="/">Kezdőlap</BNavItem>
      <BNavItem href="/rules">Szabályok</BNavItem>
      <BNavItem href="/leaderboard">Ranglista</BNavItem>
    </BNavbarNav>
    <BNavbarNav class="ml-auto">
      <BNavItemDropdown text="username">
        <BDropdownItem href="/profile">Profil</BDropdownItem>
        <BDropdownItem href="/logout">Kijelentkezés</BDropdownItem>
      </BNavItemDropdown>
    </BNavbarNav>
  </BNavbar>
  <RouterView />
  <footer>
    <img src="https://vuejs.org/images/logo.png" alt="Vue.js logo" />
    <p style="text-align: right; color: white">&copy;LopósG kártyajáték</p>
  </footer>
</template>

<script setup>
import { RouterView } from 'vue-router';
import { useUsernameStore } from './stores/username.js';
const username_store = useUsernameStore();

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
