// FILE: src/stores/websocket.js

import { defineStore } from 'pinia';

/**
 * WebSocket store a WebSocket kapcsolat és a játék állapotának kezelésére.
 */
export const useWebSocketStore = defineStore('websocket', {
  state: () => ({
    socket: null,
    gamestate: {
      card_pool: [],
      players: [],
      cards: [],
    },
    error: null,
  }),
  actions: {
    /**
     * WebSocket inicializálása és eseménykezelők beállítása.
     */
    initWebSocket() {
      if (this.socket) return;

      this.socket = new WebSocket('ws://localhost:5000/ws');

      this.socket.onopen = () => {
        console.log('Kapcsolódva a WebSockethez');
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket hiba:', error);
        this.error = 'WebSocket hiba történt.';
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.action === 'gamestate') {
            this.gamestate = message.gamestate;
            console.log('Gamestate frissült:', this.gamestate);
          } else if (message.error) {
            console.error('Hiba:', message.error);
            this.error = message.error;
          }
        } catch (e) {
          console.error('Hiba az üzenet feldolgozása során:', e);
        }
      };

      this.socket.onclose = () => {
        console.log('WebSocket kapcsolat lezárva');
        // Újracsatlakozás 5 másodperccel később
        setTimeout(() => {
          this.initWebSocket();
        }, 5000);
      };
    },

    /**
     * Üzenet küldése a WebSocket-en keresztül.
     * @param {string} action - Az üzenet akciója.
     * @param {object} payload - Az üzenet tartalma.
     */
    async sendMessage(action, payload) {
      if (!this.socket) {
        console.error('WebSocket nincs inicializálva.');
        return;
      }

      if (this.socket.readyState === WebSocket.OPEN) {
        const message = { action, ...payload };
        this.socket.send(JSON.stringify(message));
      } else if (this.socket.readyState === WebSocket.CONNECTING) {
        await new Promise((resolve, reject) => {
          this.socket.onopen = resolve;
          this.socket.onerror = reject;
        });
        const message = { action, ...payload };
        this.socket.send(JSON.stringify(message));
      } else {
        console.error('WebSocket nincs nyitva.');
      }
    },

    /**
     * Szobához való csatlakozás.
     * @param {string} roomId - A szoba azonosítója.
     * @param {string} userId - A felhasználó azonosítója.
     */
    async joinRoom(roomId, userId) {
      await this.sendMessage('join', { room_id: roomId, user_id: userId });
    },

    /**
     * Lap húzása a szobában.
     * @param {string} roomId - A szoba azonosítója.
     */
    async drawCard(roomId) {
      await this.sendMessage('draw_card', { room_id: roomId });
    },
  },
});