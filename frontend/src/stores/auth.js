// FILE: src/stores/auth.js

import { defineStore } from 'pinia';

/**
 * Auth store a felhasználói autentikáció kezelésére.
 */
export const useAuthStore = defineStore('auth', {
  state: () => ({
    currentUserId: null,
  }),
  actions: {
    /**
     * Felhasználó ID-jának beállítása.
     * @param {string} id - A felhasználó azonosítója.
     */
    setUserId(id) {
      this.currentUserId = id;
    },
    /**
     * Felhasználó ID-jának törlése.
     */
    clearUserId() {
      this.currentUserId = null;
    },
  },
});