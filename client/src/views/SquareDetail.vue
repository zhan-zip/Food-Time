<template>
  <div class="page container page-section">
    <button class="btn btn-ghost" @click="$router.back()" style="margin-bottom: var(--spacing-lg);">
      &larr; 返回广场
    </button>

    <div class="detail-layout">
      <div class="detail-img">&#x1F372;</div>
      <div class="detail-body">
        <h1 class="detail-title">创意食谱 #{{ $route.params.id }}</h1>
        <p class="text-secondary">by <strong>食光用户</strong></p>
        <div class="detail-tags">
          <span class="tag tag-primary">川菜</span>
          <span class="tag tag-default">中辣</span>
          <span class="tag tag-default">30分钟</span>
        </div>

        <div class="detail-section">
          <h3>食材</h3>
          <p>鸡蛋、番茄、青椒、猪肉</p>
        </div>

        <div class="detail-section">
          <h3>调料</h3>
          <p>酱油、料酒、糖、盐、蒜</p>
        </div>

        <div class="detail-section">
          <h3>烹饪步骤</h3>
          <p>1. 猪肉切片，用料酒和酱油腌制15分钟<br/>
          2. 鸡蛋打散炒熟备用<br/>
          3. 热锅爆香蒜末，放入肉片翻炒<br/>
          4. 加入青椒和番茄翻炒至断生<br/>
          5. 加入炒好的鸡蛋，调味出锅</p>
        </div>

        <div class="detail-section">
          <h3>营养数据</h3>
          <div class="nutrition-grid">
            <div class="nutrition-item"><span class="text-muted">热量</span><strong>280kcal</strong></div>
            <div class="nutrition-item"><span class="text-muted">蛋白质</span><strong>18g</strong></div>
            <div class="nutrition-item"><span class="text-muted">脂肪</span><strong>12g</strong></div>
            <div class="nutrition-item"><span class="text-muted">碳水</span><strong>25g</strong></div>
          </div>
        </div>

        <hr class="divider" />

        <!-- 评论区占位 -->
        <h3>评论区</h3>
        <p class="text-muted text-sm">评论功能将在 P2 阶段实现</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: var(--spacing-xl);
}
.detail-img {
  height: 260px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 64px;
}
.detail-title {
  font-size: var(--font-size-2xl);
  margin-bottom: 4px;
}
.detail-tags {
  display: flex;
  gap: var(--spacing-sm);
  margin: var(--spacing-md) 0;
}
.detail-section {
  margin-bottom: var(--spacing-lg);
}
.detail-section h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
  color: var(--color-primary-dark);
}
.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}
.nutrition-item {
  text-align: center;
  padding: var(--spacing-sm);
  background: var(--color-bg-warm);
  border-radius: var(--radius-sm);
}
.nutrition-item span {
  display: block;
  font-size: var(--font-size-xs);
}
.nutrition-item strong {
  font-size: var(--font-size-lg);
  color: var(--color-primary-dark);
}
@media (max-width: 768px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
  .nutrition-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
