<template>
  <img v-if="url" :src="url" :alt="name" class="food-img" loading="lazy" @error="onError" />
  <span v-else class="food-emoji">🍽️</span>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import request from '../api/request'

const props = defineProps({
  name: { type: String, default: '' },
  // 本地 AI 图缺失时是否回退 Pixabay（广场/首页用 true；TodayEat 用 false 直接降级 emoji）
  usePixabay: { type: Boolean, default: true },
})
const url = ref('')

// 与后端 generate_images.py safe_name 保持一致的文件名清洗
function safeName(name) {
  return String(name).replace(/[\\/:*?"<>|\s]+/g, '_')
}

// 优先使用本地 AI 生成图（server/static/food_img/菜名.png）
function localUrl(name) {
  return `/static/food_img/${encodeURIComponent(safeName(name))}.png`
}

// 本地图不存在时回退到 Pixabay 代理图
async function fallbackPixabay() {
  try {
    const res = await request.get('/foods/image', { params: { query: props.name } })
    url.value = res.url || ''
  } catch {
    url.value = ''
  }
}

function onError() {
  if (url.value.startsWith('/static/')) {
    // 本地 AI 图缺失 → 按开关回退
    url.value = ''
    if (props.usePixabay) fallbackPixabay()
    // usePixabay=false 时保持空 → 渲染 emoji
  } else {
    // Pixabay 也失败 → emoji
    url.value = ''
  }
}

function load() {
  if (!props.name) return
  url.value = localUrl(props.name)
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
