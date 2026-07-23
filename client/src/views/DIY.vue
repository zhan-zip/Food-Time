<template>
  <div class="page container page-section">
    <h2 class="section-title">我的厨房</h2>

    <div class="diy-layout">
      <!-- 食材篮子 -->
      <div class="diy-panel">
        <h3>&#x1F96C; 食材篮子</h3>
        <div class="ingredient-grid">
          <button
            v-for="item in ingredients"
            :key="item"
            class="ingredient-btn"
            @click="addToPot(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>

      <!-- 锅中区域 -->
      <div class="diy-panel diy-pot">
        <h3>&#x1F373; 你的锅中</h3>
        <div v-if="pot.length === 0" class="pot-empty">
          <span>&#x1F944;</span>
          <p class="text-muted text-sm">从左侧拖入食材和调料开始创作</p>
        </div>
        <div v-else class="pot-items">
          <span class="pot-item" v-for="(item, idx) in pot" :key="idx">
            {{ item }}
            <button class="pot-remove" @click="removeFromPot(idx)">&times;</button>
          </span>
        </div>
      </div>
    </div>

    <!-- 调料台 -->
    <div class="diy-panel" style="margin-top: var(--spacing-lg);">
      <h3>&#x1F9C2; 调料台</h3>
      <div class="ingredient-grid">
        <button
          v-for="item in seasonings"
          :key="item"
          class="ingredient-btn seasoning-btn"
          @click="addToPot(item)"
        >
          {{ item }}
        </button>
      </div>
    </div>

    <!-- 操作 -->
    <div v-if="pot.length > 0" class="diy-actions">
      <button class="btn btn-primary btn-lg" @click="askAI">
        &#x1F916; 我做好了，AI 给点建议
      </button>
    </div>

    <!-- AI 建议 -->
    <div v-if="aiSuggestion" class="card" style="margin-top: var(--spacing-lg);">
      <h3>&#x1F4AC; AI 烹饪建议</h3>
      <p style="white-space: pre-wrap;">{{ aiSuggestion }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const ingredients = ['鸡蛋', '番茄', '土豆', '青椒', '猪肉', '牛肉', '虾仁', '豆腐', '白菜', '香菇', '胡萝卜', '洋葱']
const seasonings = ['盐', '酱油', '醋', '料酒', '糖', '蒜', '姜', '葱', '辣椒', '花椒', '食用油', '蚝油']

const pot = ref([])
const aiSuggestion = ref('')

function addToPot(item) {
  if (!pot.value.includes(item)) {
    pot.value.push(item)
  }
}

function removeFromPot(idx) {
  pot.value.splice(idx, 1)
  aiSuggestion.value = ''
}

function askAI() {
  aiSuggestion.value = 'AI 烹饪建议功能将在 P2 阶段接入 DeepSeek。\n当前食材：' + pot.value.join('、') + '\n\n建议烹饪方式：根据你的食材组合，AI 将分析并推荐科学健康的烹饪方法，包括火候、时间和预估营养数据。'
}
</script>

<style scoped>
.diy-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}
.diy-panel {
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}
.diy-panel h3 {
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-base);
}
.ingredient-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}
.ingredient-btn {
  padding: 6px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-bg-card);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--color-text);
}
.ingredient-btn:hover {
  border-color: var(--color-primary);
  background: rgba(217, 161, 91, 0.08);
  color: var(--color-primary-dark);
}
.seasoning-btn:hover {
  border-color: var(--color-primary-dark);
}
.pot-empty {
  text-align: center;
  padding: 40px 0;
  font-size: 48px;
}
.pot-items {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}
.pot-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: rgba(217, 161, 91, 0.12);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  color: var(--color-primary-dark);
}
.pot-remove {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  color: var(--color-text-muted);
  padding: 0 2px;
}
.diy-actions {
  text-align: center;
  margin-top: var(--spacing-xl);
}
@media (max-width: 640px) {
  .diy-layout {
    grid-template-columns: 1fr;
  }
}
</style>
