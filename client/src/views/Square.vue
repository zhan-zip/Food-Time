<template>
  <div class="page container page-section">
    <h2 class="section-title">美食广场</h2>
    <p class="text-secondary mb-lg">发现其他食光记用户分享的创意食谱，找到属于你的烹饪灵感</p>

    <div class="square-grid">
      <div class="card square-card" v-for="n in 6" :key="n" @click="$router.push(`/square/${n}`)">
        <div class="square-img">&#x1F372;</div>
        <div class="square-info">
          <h3>创意食谱示例 {{ n }}</h3>
          <p class="text-sm text-muted">by 食光用户</p>
          <div class="square-stats text-xs text-muted">
            <span>&#x2764; {{ n * 7 }}</span>
            <span>&#x2B50; {{ n * 3 }}</span>
          </div>
        </div>
      </div>
    </div>

    <p class="text-center text-muted text-sm" style="margin-top: var(--spacing-xl);">
      广场功能将在 P2 阶段实现，届时可查看和分享真实用户食谱
    </p>
  </div>
</template>

<style scoped>
.mb-lg { margin-bottom: var(--spacing-lg); }
.square-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.square-card {
  cursor: pointer;
}
.square-img {
  height: 160px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  margin-bottom: var(--spacing-md);
}
.square-info h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 2px;
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
