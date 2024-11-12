import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useRoomIdStore = defineStore('room_id', () => {
  const room_id = ref('')

  return { room_id }
})
