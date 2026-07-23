<template>
  <div style="min-height: 100vh; background: var(--color-bg);">
    <header style="background: var(--color-bg-card); border-bottom: 1px solid var(--color-divider); padding: 16px 0;">
      <div class="container flex justify-between items-center">
        <h2 style="font-size: var(--font-size-lg); font-weight: 700;">管理后台</h2>
        <router-link to="/" class="btn btn-ghost btn-sm">返回首页</router-link>
      </div>
    </header>

    <div class="container" style="padding-top: var(--spacing-xl); padding-bottom: var(--spacing-xl);">
      <!-- 数据统计 -->
      <div class="stats-row">
        <div class="card stat-card">
          <span class="stat-value">{{ stats.users }}</span>
          <span class="stat-label">注册用户</span>
        </div>
        <div class="card stat-card">
          <span class="stat-value">{{ stats.foods }}</span>
          <span class="stat-label">食物条目</span>
        </div>
        <div class="card stat-card">
          <span class="stat-value">{{ stats.recipes }}</span>
          <span class="stat-label">食谱数量</span>
        </div>
      </div>

      <!-- 管理功能 -->
      <div class="card" style="margin-top: var(--spacing-lg);">
        <h3>用户管理</h3>
        <p class="text-muted text-sm">功能将在 P3 阶段实现</p>
      </div>

      <div class="card" style="margin-top: var(--spacing-md);">
        <h3>食谱审核</h3>
        <p class="text-muted text-sm">功能将在 P3 阶段实现</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const stats = ref({ users: 0, foods: 20, recipes: 0 })
</script>

<style scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.stat-card {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
}
.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--color-primary-dark);
  display: block;
}
.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}
@media (max-width: 640px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}
</style>
