<template>
  <div v-if="stage === 'selecting' && canSuggest" class="suggest-trigger">
    <button class="btn btn-primary" style="width:100%" :disabled="loading" @click="$emit('suggest')">
      {{ loading ? 'AI 分析中...' : '🤖 获取 AI 烹饪建议' }}
    </button>
  </div>

  <!-- 建议结果 -->
  <div v-if="stage === 'suggesting' || aiSuggestion || matchedRecipes.length || suggestError" class="card suggestion-card">
    <div v-if="stage === 'suggesting'" class="text-center text-muted text-sm" style="padding:20px">AI 正在分析食材组合...</div>

    <!-- 数据库匹配 -->
    <div v-if="matchedRecipes.length > 0" class="match-section">
      <h4 class="match-title">📋 发现相似菜谱（食材匹配）</h4>
      <div class="match-list">
        <div v-for="r in matchedRecipes" :key="r.id" class="match-item">
          <div class="match-name">{{ r.name }}</div>
          <div class="match-meta">
            <span class="tag tag-default">{{ r.cuisine || '通用' }}</span>
            <span class="text-xs text-muted">匹配 {{ r.match_count }} 种食材</span>
            <span v-if="r.calories_per_100g" class="text-xs text-muted">{{ r.calories_per_100g }}千卡/100g</span>
          </div>
        </div>
      </div>
    </div>

    <!-- AI 建议 -->
    <div v-if="aiSuggestion" class="ai-section">
      <h4 class="ai-title">🧑‍🍳 {{ aiSuggestion.name }}</h4>
      <p class="ai-meta">
        <span class="tag tag-primary">{{ aiSuggestion.cooking_method_label || '炒锅' }}</span>
        <span class="text-sm text-muted">约 {{ aiSuggestion.estimated_time || '-' }} · {{ aiSuggestion.estimated_calories || '-' }}千卡/100g</span>
      </p>
      <div v-if="aiSuggestion.steps?.length" class="ai-steps">
        <div v-for="(s, i) in aiSuggestion.steps" :key="i" class="ai-step">
          <span class="step-num">{{ i + 1 }}</span>
          <span>{{ s }}</span>
        </div>
      </div>
      <p v-if="aiSuggestion.nutrition_tip" class="ai-tip text-sm">💡 {{ aiSuggestion.nutrition_tip }}</p>
      <p class="nutrition-source text-xs text-muted">营养数据来源：中国食物成分表（第六版）- 基于食材加权估算</p>
    </div>

    <!-- 错误 -->
    <div v-if="suggestError" class="text-sm" style="color:#e74c3c">{{ suggestError }}</div>

    <!-- 操作按钮 -->
    <div v-if="aiSuggestion || matchedRecipes.length" class="suggest-actions">
      <button class="btn btn-outline" @click="$emit('skip')">跳过动画，直接烹饪</button>
      <button class="btn btn-primary" @click="$emit('cook')">🔥 开始烹饪</button>
    </div>
  </div>

  <!-- 烹饪方式选择 + 动画 -->
  <div v-if="stage === 'cooking'" class="card cooking-card">
    <h4 class="cooking-title">选择烹饪方式</h4>
    <div class="method-btns">
      <button
        v-for="m in cookingMethods"
        :key="m.key"
        class="method-btn"
        :class="{ active: cookingMethod === m.key }"
        @click="$emit('select-method', m.key)"
      >
        <span class="method-label">{{ m.label }}</span>
        <span class="method-desc">{{ m.desc }}</span>
      </button>
    </div>

    <!-- 动画播放区 -->
    <div v-if="showAnimation" class="animation-area">
      <!-- 炒锅动画 -->
      <div v-if="cookingMethod === 'wok'" class="anim-wok">
        <span class="pot-emoji">🍳</span>
        <div class="flame-container">
          <span v-for="i in 8" :key="i" class="flame-particle" :style="{ animationDelay: (i * 0.15) + 's' }"></span>
        </div>
        <p class="anim-hint">大火翻炒中...</p>
      </div>
      <!-- 空气炸锅动画 -->
      <div v-if="cookingMethod === 'air_fryer'" class="anim-airfryer">
        <span class="pot-emoji">🔥</span>
        <div class="heat-waves">
          <span v-for="i in 3" :key="i" class="heat-wave" :style="{ animationDelay: (i * 0.4) + 's' }"></span>
        </div>
        <p class="anim-hint">循环热风中...</p>
      </div>
      <!-- 蒸锅动画 -->
      <div v-if="cookingMethod === 'steamer'" class="anim-steamer">
        <span class="pot-emoji">♨️</span>
        <div class="steam-container">
          <span v-for="i in 6" :key="i" class="steam-particle" :style="{ left: (20 + i * 10) + '%', animationDelay: (i * 0.3) + 's' }"></span>
        </div>
        <p class="anim-hint">蒸汽烹饪中...</p>
      </div>

      <button class="btn btn-outline btn-sm skip-btn" @click="$emit('skip-animation')">跳过动画 → 保存</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stage: { type: String, default: 'selecting' },
  canSuggest: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  aiSuggestion: { type: Object, default: null },
  matchedRecipes: { type: Array, default: () => [] },
  suggestError: { type: String, default: '' },
  cookingMethod: { type: String, default: 'wok' },
  cookingMethods: { type: Array, default: () => [] },
  showAnimation: { type: Boolean, default: false },
})

defineEmits(['suggest', 'cook', 'skip', 'select-method', 'skip-animation'])
</script>

<style scoped>
.suggest-trigger { margin-bottom: var(--spacing-md); }
.suggestion-card { padding: var(--spacing-md); }
.match-section { margin-bottom: var(--spacing-md); }
.match-title { font-size: var(--font-size-sm); font-weight: 600; margin-bottom: 8px; }
.match-list { display: flex; flex-direction: column; gap: 8px; }
.match-item { padding: 8px; background: var(--color-bg); border-radius: var(--radius-sm); }
.match-name { font-size: var(--font-size-sm); font-weight: 500; }
.match-meta { display: flex; gap: 8px; align-items: center; margin-top: 4px; }
.ai-section { margin-bottom: var(--spacing-sm); }
.ai-title { font-size: var(--font-size-base); font-weight: 600; margin-bottom: 4px; }
.ai-meta { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.ai-steps { display: flex; flex-direction: column; gap: 6px; margin-bottom: 8px; }
.ai-step { display: flex; gap: 8px; font-size: var(--font-size-sm); line-height: 1.5; }
.step-num { width: 20px; height: 20px; border-radius: 50%; background: var(--color-primary); color: white; text-align: center; font-size: 11px; line-height: 20px; flex-shrink: 0; }
.ai-tip { color: var(--color-primary-dark); margin-bottom: 4px; }
.nutrition-source { font-style: italic; }
.suggest-actions { display: flex; gap: 8px; margin-top: var(--spacing-md); }
.suggest-actions .btn { flex: 1; }

/* 烹饪方式 */
.cooking-card { padding: var(--spacing-md); }
.cooking-title { font-size: var(--font-size-sm); font-weight: 600; margin-bottom: 8px; }
.method-btns { display: flex; gap: 8px; margin-bottom: var(--spacing-md); }
.method-btn { flex: 1; padding: 10px; border: 2px solid var(--color-border); border-radius: var(--radius-md); background: var(--color-bg-card); cursor: pointer; transition: all 0.2s; text-align: center; }
.method-btn:hover { border-color: var(--color-primary); }
.method-btn.active { border-color: var(--color-primary); background: rgba(217,161,91,0.08); }
.method-label { display: block; font-size: var(--font-size-sm); font-weight: 600; }
.method-desc { display: block; font-size: 11px; color: var(--color-text-muted); margin-top: 2px; }

/* 动画区 */
.animation-area { text-align: center; padding: 20px 0; position: relative; min-height: 120px; }
.pot-emoji { font-size: 48px; display: block; margin-bottom: 8px; }
.anim-hint { font-size: var(--font-size-sm); color: var(--color-text-muted); margin-top: 8px; }

/* 火焰 */
.flame-container { position: relative; height: 30px; }
.flame-particle {
  position: absolute; bottom: 0; width: 14px; height: 20px;
  background: linear-gradient(to top, #e74c3c, #f39c12, transparent);
  border-radius: 50% 50% 20% 20%;
  animation: flameDance 0.7s ease-in-out infinite alternate;
  left: calc(50% - 7px);
}
@keyframes flameDance {
  0% { transform: translateY(0) scale(1, 0.8); opacity: 0.9; }
  100% { transform: translateY(-14px) scale(0.6, 1.2); opacity: 0.4; }
}

/* 热风波纹 */
.heat-waves { position: relative; height: 30px; }
.heat-wave {
  position: absolute; width: 40px; height: 2px;
  background: linear-gradient(to right, transparent, #e67e22, transparent);
  left: calc(50% - 20px);
  animation: heatRise 1.2s ease-out infinite;
}
@keyframes heatRise {
  0% { transform: translateY(10px); opacity: 0.8; }
  100% { transform: translateY(-20px); opacity: 0; }
}

/* 蒸汽 */
.steam-container { position: relative; height: 60px; }
.steam-particle {
  position: absolute; bottom: 0; width: 8px; height: 8px;
  background: rgba(255,255,255,0.7); border-radius: 50%;
  animation: steamRise 2s ease-out infinite;
}
@keyframes steamRise {
  0% { transform: translateY(0) scale(0.5); opacity: 0.6; }
  100% { transform: translateY(-50px) scale(1.8); opacity: 0; }
}

.skip-btn { margin-top: 12px; font-size: 11px; }
</style>
