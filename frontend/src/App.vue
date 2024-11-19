<template>
  <BNavbar variant="dark" v-b-color-mode="'dark'" class="navbar">
    <BNavbarNav>
      <BNavItem href="/">Kezdőlap</BNavItem>

      <BNavItemDropdown :text="username_store.username" right>
        <BDropdownItem href="/profile">Profil</BDropdownItem>
        <BDropdownItem href="/logout">Kijelentkezés</BDropdownItem>
      </BNavItemDropdown>

    </BNavbarNav>
  </BNavbar>
  <RouterView />
  <footer>
    <div style="display: flex; align-items: center;">
      <img src="@/assets/logo.svg" alt="Vue logo" />
      <p style="margin-left: 10px;">LopósG kártyajáték &copy; 2024</p>
    </div>
  </footer>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { ref } from 'vue';
import { useUsernameStore } from './stores/username';

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

footer img {
  width: 50px;
}
</style>
