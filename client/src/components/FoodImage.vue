<template>
  <img v-if="url" :src="url" :alt="name" class="food-img" loading="lazy" @error="url = ''" />
  <span v-else class="food-emoji">🍽️</span>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import request from '../api/request'

const props = defineProps({ name: { type: String, default: '' } })
const url = ref('')

async function load() {
  if (!props.name) return
  try {
    const res = await request.get('/foods/image', { params: { query: props.name } })
    url.value = res.url || ''
  } catch {
    url.value = ''
  }
}

onMounted(load)
watch(() => props.name, load)
</script>

<style scoped>
.food-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border-radius: inherit;
}
.food-emoji {
  font-size: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
