// FILE: src/stores/room_id.js

import { defineStore } from 'pinia';

/**
 * Room ID store az aktuális szoba azonosítójának kezelésére.
 */
export const useRoomIdStore = defineStore('room_id', {
  state: () => ({
    roomId: '',
  }),
  actions: {
    /**
     * Szoba ID beállítása.
     * @param {string} id - A szoba azonosítója.
     */
    setRoomId(id) {
      this.roomId = id;
    },
    /**
     * Szoba ID törlése.
     */
    clearRoomId() {
      this.roomId = '';
    },
  },
});