<template>
  <div class="page container page-section">
    <h2 class="section-title">美食广场</h2>
    <p class="text-secondary mb-lg">发现其他食光记用户分享的创意食谱，找到属于你的烹饪灵感</p>

    <!-- 加载中 -->
    <div v-if="loading" class="text-center" style="padding: 60px 0;">
      <p>加载中...</p>
    </div>

    <!-- 食谱列表 -->
    <div v-else-if="recipes.length > 0" class="square-grid">
      <div
        class="card square-card"
        v-for="r in recipes"
        :key="r.id"
        @click="$router.push(`/square/${r.id}`)"
      >
        <div class="square-img">
          <img v-if="r.image_url" :src="r.image_url" :alt="r.name" />
          <span v-else>&#x1F372;</span>
        </div>
        <div class="square-info">
          <h3>{{ r.name }}</h3>
          <p class="text-sm text-muted">by {{ r.author }}</p>
          <div class="square-tags" v-if="r.cuisine">
            <span class="tag tag-default tag-xs">{{ r.cuisine }}</span>
          </div>
          <div class="square-stats text-xs text-muted">
            <span>&#x2764; {{ r.like_count }}</span>
            <span>&#x2B50; {{ r.fav_count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="text-center" style="padding: 60px 0;">
      <p class="text-secondary">还没有人分享食谱，快来成为第一个吧！</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecipes } from '../api/public'

const recipes = ref([])
const loading = ref(true)

async function fetchRecipes() {
  loading.value = true
  try {
    const res = await getRecipes()
    recipes.value = res.items || []
  } catch (e) {
    console.error('加载食谱列表失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchRecipes)
</script>

<style scoped>
.mb-lg { margin-bottom: var(--spacing-lg); }
.square-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.square-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.square-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.square-img {
  height: 160px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  overflow: hidden;
  background: var(--color-bg-warm);
}
.square-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.square-info h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.square-tags {
  margin: var(--spacing-xs) 0;
}
.tag-xs {
  font-size: 11px;
  padding: 1px 6px;
}
.square-stats {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}
@media (max-width: 768px) {
  .square-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 480px) {
  .square-grid {
    grid-template-columns: 1fr;
  }
}
</style>
