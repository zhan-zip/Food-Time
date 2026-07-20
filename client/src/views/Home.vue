<template>
  <div class="home-page">
    <van-nav-bar title="Food-Time" fixed />

    <div class="home-content">
      <!-- 欢迎卡片 -->
      <div class="welcome-card">
        <h2>你好，{{ user?.nickname || '用户' }}</h2>
        <p>今天想吃点什么？</p>
      </div>

      <!-- 快捷入口 -->
      <van-grid :column-num="3" :gutter="12" class="quick-actions">
        <van-grid-item
          v-for="action in actions"
          :key="action.text"
          :icon="action.icon"
          :text="action.text"
          @click="action.onClick"
        />
      </van-grid>

      <!-- 食物推荐 -->
      <van-cell-group title="今日推荐" inset>
        <van-cell
          v-for="food in recommendedFoods"
          :key="food.id"
          :title="food.name"
          :label="food.cuisine + ' | ' + (food.calories_per_100g || '?') + ' kcal/100g'"
          is-link
          @click="showFoodDetail(food)"
        />
        <van-cell v-if="!recommendedFoods.length" title="加载中..." />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getMe } from '../api/auth'
import request from '../api/request'

const router = useRouter()
const user = ref(null)
const recommendedFoods = ref([])

const actions = [
  { text: '食物库', icon: 'search', onClick: () => router.push('/food') },
  { text: 'AI 对话', icon: 'chat-o', onClick: () => router.push('/chat') },
  { text: '记账', icon: 'balance-o', onClick: () => router.push('/expense') },
]

onMounted(async () => {
  try {
    user.value = await getMe()
  } catch { /* ignored */ }

  try {
    const res = await request.get('/foods', { params: { page_size: 5 } })
    recommendedFoods.value = res.items || []
  } catch { /* ignored */ }
})

function showFoodDetail(food) {
  showToast(food.name + '\n' + (food.cuisine || '') + ' | ' + (food.calories_per_100g || '?') + ' kcal/100g')
}
</script>

<style scoped>
.home-page {
  padding-top: 46px;
}
.home-content {
  padding: 12px;
}
.welcome-card {
  background: linear-gradient(135deg, #4CAF50, #81C784);
  color: #fff;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 16px;
}
.welcome-card h2 {
  margin: 0 0 8px;
  font-size: 24px;
}
.welcome-card p {
  margin: 0;
  opacity: 0.9;
}
.quick-actions {
  margin-bottom: 16px;
}
</style>
