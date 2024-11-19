import { ref, computed } from 'vue'
import { defineStore } from 'pinia';

export const useUsernameStore = defineStore('username', () => {
  const username = ref('')
  return { username }
})