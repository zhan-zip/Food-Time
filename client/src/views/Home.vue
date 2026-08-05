<template>
  <div class="page-home">
    <!-- Banner：整张美食图做背景，文字叠图 + 底部过渡渐变（图与背景融为一体） -->
    <section class="hero-banner">
      <div class="hero-slide container">
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

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getRecipes } from '../api/public'
import FoodImage from '../components/FoodImage.vue'
import { maybeStartOnboarding } from '../utils/onboarding'

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
  // 新用户首次登录：触发引导（等 DOM 渲染完，导航元素已就绪）
  nextTick(() => maybeStartOnboarding())
})
</script>

<style scoped>
/* Banner：整张美食图做背景，文字叠图 + 底部过渡渐变（图与背景融为一体） */
.hero-banner {
  min-height: 620px;
  display: flex;
  align-items: flex-end;
  padding: 48px 0 44px;
  background:
    linear-gradient(180deg, rgba(20, 10, 5, 0) 42%, rgba(20, 10, 5, 0.28) 65%, rgba(20, 10, 5, 0.84) 100%),
    url('/static/hero-dish.png');
  background-size: cover;
  background-position: center;
}
.hero-slide {
  width: 100%;
}
.hero-text {
  max-width: 560px;
}
.hero-text h1 {
  font-family: "Songti SC", "SimSun", "STSong", Georgia, serif;
  font-size: 56px;
  font-weight: 700;
  color: #fff;
  line-height: 1.15;
  margin-bottom: 12px;
  letter-spacing: 2px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.hero-desc {
  font-size: var(--font-size-lg);
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 24px;
  line-height: 1.7;
}
.hero-actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}
/* 图上：白色按钮，高对比 */
.hero-actions .btn-primary {
  background: #fff;
  color: #241510;
  border: 1px solid #fff;
  font-weight: 600;
}
.hero-actions .btn-primary:hover {
  background: #F5EDE3;
}
.hero-actions .btn-outline {
  border-color: rgba(255, 255, 255, 0.85);
  color: #fff;
}
.hero-actions .btn-outline:hover {
  background: rgba(255, 255, 255, 0.12);
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

@media (max-width: 768px) {
  .hero-banner {
    min-height: 480px;
    padding: 32px 0 28px;
  }
  .hero-text {
    max-width: 100%;
    text-align: center;
  }
  .hero-desc {
    margin: 0 auto 20px;
  }
  .hero-actions {
    justify-content: center;
  }
  .hero-text h1 {
    font-size: 40px;
    letter-spacing: 1px;
  }
  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
