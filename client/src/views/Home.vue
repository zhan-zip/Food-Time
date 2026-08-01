<template>
  <div class="page-home">
    <!-- Banner 轮播区 -->
    <section class="hero-banner">
      <div class="hero-slide container">
        <span class="hero-emoji">🍽️</span>
        <div class="hero-text">
          <h1>今天吃什么？</h1>
          <p class="hero-desc">食光记 — AI 驱动的智能饮食助手，帮您解决每一刻的选择困难</p>
          <div class="hero-actions">
            <router-link to="/today-eat" class="btn btn-primary btn-lg">开始探索</router-link>
            <router-link to="/assistant" class="btn btn-outline btn-lg">问问 AI</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- 每日推送 -->
    <section class="page-section">
      <div class="container">
        <h2 class="section-title">每日推荐</h2>
        <p v-if="recommendLoading" class="text-sm text-muted" style="text-align:center; padding: 30px 0">加载推荐中...</p>
        <div v-else-if="recommended.length === 0" class="recommend-grid">
          <div class="card recommend-card">
            <div class="recommend-img-placeholder">🍲</div>
            <div class="recommend-info">
              <h3>暂无推荐</h3>
              <p class="text-sm text-secondary">去广场分享你的第一道菜吧</p>
            </div>
          </div>
        </div>
        <div v-else class="recommend-grid">
          <router-link v-for="r in recommended" :key="r.id" :to="'/square/' + r.id" class="card recommend-card">
            <div class="recommend-img-placeholder"><FoodImage :name="r.name" /></div>
            <div class="recommend-info">
              <h3>{{ r.name }}</h3>
              <p class="text-sm text-secondary">{{ r.cuisine || '家常' }}<template v-if="r.calories"> · {{ r.calories }} kcal/100g</template></p>
              <span class="tag tag-primary">广场精选 · ❤️{{ r.like_count || 0 }}</span>
            </div>
          </router-link>
        </div>
      </div>
    </section>

    <!-- 功能介绍 -->
    <section class="page-section" style="background: var(--color-bg-warm);">
      <div class="container">
        <h2 class="section-title">怎么用食光记</h2>
        <div class="feature-grid">
          <div class="card feature-card" v-for="(f, i) in features" :key="i">
            <span class="feature-icon">{{ f.icon }}</span>
            <h3>{{ f.title }}</h3>
            <p class="text-sm text-secondary">{{ f.desc }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getRecipes } from '../api/public'
import FoodImage from '../components/FoodImage.vue'

const features = [
  { icon: '\u{1F50D}', title: '食物决策', desc: '筛选、转盘、AI推荐，三种方式帮你快速决定吃什么' },
  { icon: '\u{1F52A}', title: '我的厨房', desc: '拖拽食材制作自定义食谱，AI 提供专业烹饪建议' },
  { icon: '\u{1F30D}', title: '美食广场', desc: '分享你的创意食谱，发现他人的美味灵感' },
  { icon: '\u{1F4B0}', title: '智能记账', desc: '手动录入或拍照识别账单，自动生成消费图表' },
  { icon: '\u{1F916}', title: 'AI 助手', desc: '多轮对话，长期记忆，随时提供饮食分析和建议' },
  { icon: '\u{1F4CA}', title: '营养分析', desc: '记录每日饮食，雷达图和柱状图展示营养摄入趋势' },
]

// 视觉美化：每日推荐取广场最近 3 个已审核菜谱（替代静态占位）
const recommended = ref([])
const recommendLoading = ref(true)

onMounted(async () => {
  try {
    const res = await getRecipes(1, 3, { sort_by: 'time', order: 'desc' })
    recommended.value = res.items || []
  } catch (e) {
    console.error('加载推荐失败', e)
  } finally {
    recommendLoading.value = false
  }
})
</script>

<style scoped>
/* Banner */
.hero-banner {
  background: linear-gradient(135deg, #D9A15B 0%, #D8B08C 40%, #F5EDE3 100%);
  padding: 60px 0;
}
.hero-slide {
  text-align: center;
  position: relative;
}
.hero-emoji {
  display: block;
  font-size: 72px;
  margin-bottom: 8px;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.12));
}
.hero-text h1 {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 12px;
}
.hero-desc {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  max-width: 480px;
  margin: 0 auto 24px;
  line-height: 1.7;
}
.hero-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

/* 每日推荐 */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.recommend-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  text-decoration: none;
  display: block;
}
.recommend-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}
.recommend-img-placeholder {
  height: 160px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin-bottom: var(--spacing-md);
}
.recommend-info h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 4px;
}
.recommend-info p {
  margin-bottom: var(--spacing-sm);
}

/* 功能介绍 */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.feature-card {
  text-align: center;
}
.feature-icon {
  font-size: 36px;
  margin-bottom: var(--spacing-sm);
  display: block;
}
.feature-card h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

@media (max-width: 768px) {
  .hero-banner {
    padding: 40px 0;
  }
  .hero-text h1 {
    font-size: var(--font-size-2xl);
  }
  .recommend-grid,
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
</style>
