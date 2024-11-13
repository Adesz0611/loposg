<!-- FILE: src/views/HomeView.vue -->

<template>
  <div>
    <button @click="login">Login</button>
    <button @click="logout">Logout</button>
    <button @click="createRoom">Szoba létrehozása</button>
    <button @click="getCard">Lap húzás</button>
    <textarea v-model="joinText" placeholder="Szoba azonosító"></textarea>
    <button @click="joinRoom">Csatlakozás a szobához</button>
    <p>Card: {{ card }}</p>
    <p>Room ID: {{ roomId }}</p>
    <button @click="fetchRooms">Szobák lekérése</button>
    <p>Aktuális szoba: {{ roomIdStore.roomId }}</p>

    <!-- GameRoom komponens beillesztése -->
    <GameRoom
      v-if="authStore.currentUserId && roomIdStore.roomId"
      :roomId="roomIdStore.roomId"
      :userId="authStore.currentUserId"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useRoomIdStore } from '../stores/room_id';
import { useWebSocketStore } from '../stores/websocket';
import { useAuthStore } from '../stores/auth';
import GameRoom from '../components/GameRoom.vue';

const roomId = ref('');
const card = ref('');
const joinText = ref('');

const roomIdStore = useRoomIdStore();
const wsStore = useWebSocketStore();
const authStore = useAuthStore();

const router = useRouter();

/**
 * Bejelentkezés a backend szerver felé, majd átirányítás az autentikáció URL-jére.
 */
function login() {
  axios
    .get('http://localhost:5000/login')
    .then((response) => {
      window.location.href = response.data.auth_url;
    })
    .catch((error) => {
      console.error('Login hiba:', error);
    });
}

/**
 * Kijelentkezés a backend szerver felé, tokenek törlése és store frissítése.
 */
function logout() {
  axios
    .post('http://localhost:5000/logout', {
      token_refresh: localStorage.getItem('refresh_token'),
    })
    .then(() => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('isUserLoggedIn');
      authStore.clearUserId();
      alert('Kijelentkeztél!');
    })
    .catch((error) => {
      console.error('Logout hiba:', error);
    });
}

/**
 * Szoba létrehozása a backend szerveren, majd navigáció a GameRoom komponensre.
 */
async function createRoom() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('Nincs érvényes token, kérlek jelentkezz be.');
    return;
  }

  try {
    const response = await axios.post(
      'http://localhost:5000/create_room',
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    roomId.value = response.data.room_id;
    roomIdStore.setRoomId(response.data.room_id);
    console.log('Szoba létrehozva:', response.data.room_id);
    // Navigálj a GameRoom komponensre
    router.push({
      name: 'GameRoom',
      params: { roomId: response.data.room_id, userId: authStore.currentUserId },
    });
  } catch (error) {
    console.error(
      'Szoba létrehozása sikertelen:',
      error.response ? error.response.data : error
    );
  }
}

/**
 * Szobák lekérése a backend szerver felől.
 */
function fetchRooms() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('Nincs érvényes token, kérlek jelentkezz be.');
    return;
  }

  axios
    .get('http://localhost:5000/rooms', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    .then((response) => {
      console.log('Szobák:', response.data.rooms);
    })
    .catch((error) => {
      console.error('Szobák lekérése sikertelen:', error);
    });
}

/**
 * Szobához való csatlakozás a backend szerveren, majd navigáció a GameRoom komponensre.
 */
async function joinRoom() {
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('Nincs érvényes token, kérlek jelentkezz be.');
    return;
  }

  try {
    const response = await axios.post(
      'http://localhost:5000/join_room',
      {
        room_id: joinText.value,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    roomIdStore.setRoomId(response.data.room_id);
    // Navigálj a GameRoom komponensre
    router.push({
      name: 'GameRoom',
      params: { roomId: response.data.room_id, userId: authStore.currentUserId },
    });
    console.log('Csatlakozás sikeres:', response.data);
  } catch (error) {
    console.error(
      'Csatlakozás sikertelen:',
      error.response ? error.response.data : error
    );
  }
}

const cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

/**
 * Véletlenszerű lap húzása.
 */
function getCard() {
  card.value = cards[Math.floor(Math.random() * cards.length)];
}

/**
 * Callback feldolgozása az autentikáció után.
 */
async function handleCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  if (code) {
    try {
      const response = await axios.post('http://localhost:5000/callback', { code });

      // Ellenőrizzük, hogy a válasz tartalmazza-e a tokeneket és a user_info-t
      if (response.data && response.data.token) {
        const { access_token, refresh_token, user_info } = response.data.token;

        // Tokenek tárolása a localStorage-ban
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('isUserLoggedIn', true);

        // AuthStore frissítése a felhasználó ID-jával
        authStore.setUserId(user_info.sub);

        console.log('Bejelentkezett felhasználó:', user_info.preferred_username);

        // Tisztítsd meg az URL-t és navigálj a Home útvonalra
        router.replace({ name: 'Home' });
      } else {
        console.error("Nem sikerült lekérni a tokent:", response.data);
      }
    } catch (error) {
      console.error('Callback feldolgozása sikertelen:', error);
    }
  }
}

onMounted(() => {
  handleCallback();
});
</script>

<style scoped>
.error {
  color: red;
  margin-top: 10px;
}
</style>