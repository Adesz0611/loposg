<!-- FILE: src/components/GameRoom.vue -->

<template>
  <div>
    <h2>Szoba: {{ roomId }}</h2>
    <button @click="drawCard">Lap húzása</button>
    <div>
      <h3>Húzott lapok:</h3>
      <ul>
        <li v-for="(card, index) in gamestate.cards" :key="index">{{ card }}</li>
      </ul>
    </div>
    <div>
      <h3>Játékosok:</h3>
      <ul>
        <li v-for="player in gamestate.players" :key="player.id">
          {{ player.name }} - Pontok: {{ player.score }}
        </li>
      </ul>
    </div>
    <div v-if="error" class="error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useWebSocketStore } from '../stores/websocket';
import { useRoomIdStore } from '../stores/room_id';

const props = defineProps({
  roomId: {
    type: String,
    required: true,
  },
  userId: {
    type: String,
    required: true,
  },
});

const wsStore = useWebSocketStore();
const roomIdStore = useRoomIdStore();

const gamestate = computed(() => wsStore.gamestate);
const error = computed(() => wsStore.error);

/**
 * WebSocket inicializálása és szobához való csatlakozás a komponens betöltésekor.
 */
onMounted(async () => {
  wsStore.initWebSocket();
  try {
    await wsStore.joinRoom(props.roomId, props.userId);
    roomIdStore.setRoomId(props.roomId);
  } catch (e) {
    console.error('Hiba a szoba csatlakozása során:', e);
  }
});

/**
 * Lap húzása a játékban.
 */
function drawCard() {
  wsStore.drawCard(props.roomId);
}
</script>

<style scoped>
.error {
  color: red;
  margin-top: 10px;
}
</style>