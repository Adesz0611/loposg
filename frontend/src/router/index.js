// FILE: src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import AboutView from '../views/AboutView.vue';
import GameRoom from '../components/GameRoom.vue';
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeView,
  },
  {
    path: '/about',
    name: 'about',
    component: AboutView,
  },
  {
    path: '/room/:roomId',
    name: 'GameRoom',
    component: GameRoom,
    props: true,
  },
  {
    path: '/callback',
    name: 'Callback',
    component: HomeView, // Opció: Külön Callback komponens létrehozása
  },
  // Egyéb útvonalak
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

/**
 * Globális router hook az autentikációs kód feldolgozására.
 */
router.beforeEach(async (to, from, next) => {
  const code = to.query.code;
  if (code) {
    try {
      const response = await axios.post('http://localhost:5000/callback', { code });
      const { access_token, refresh_token, user_info } = response.data.token;

      // Ellenőrizzük, hogy a szükséges adatok megvannak-e
      if (!access_token || !refresh_token || !user_info) {
        throw new Error('A válasz nem tartalmazza a szükséges adatokat.');
      }

      // Tokenek tárolása a localStorage-ban
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('isUserLoggedIn', true);

      // AuthStore frissítése a felhasználó ID-jával
      const authStore = useAuthStore();
      authStore.setUserId(user_info.sub);

      console.log('Bejelentkezett felhasználó:', user_info.preferred_username);

      // Tisztítsd meg az URL-t és navigálj a Home útvonalra
      next({ name: 'Home' });
    } catch (error) {
      console.error('Error during login callback:', error);
      next();
    }
  } else {
    next();
  }
});

export default router;