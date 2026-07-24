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
      <div class="nutrition-disclaimer">
        <p class="nutrition-source">📊 营养数据来源：中国食物成分表（第六版），基于食材加权估算</p>
        <p class="nutrition-warning">⚠️ AI 烹饪建议仅供参考，非医疗诊断结果。具体热量因烹饪方式和食材用量而异，请结合实际情况判断。</p>
      </div>
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
        <div class="wok-scene">
          <span class="pot-emoji">🍳</span>
          <div class="food-shake">
            <span class="food-piece" v-for="i in 5" :key="'f'+i" :style="{ animationDelay: (i * 0.2) + 's' }">🫑</span>
          </div>
          <div class="flame-layer">
            <span v-for="i in 12" :key="'fl'+i" class="flame-particle" :style="flameStyle(i)"></span>
          </div>
        </div>
        <p class="anim-hint">🔥 大火翻炒中...</p>
      </div>

      <!-- 空气炸锅动画 -->
      <div v-if="cookingMethod === 'air_fryer'" class="anim-airfryer">
        <div class="airfryer-scene">
          <span class="pot-emoji">🔥</span>
          <div class="air-circulation">
            <span v-for="i in 8" :key="'ac'+i" class="air-dot" :style="{ animationDelay: (i * 0.25) + 's' }"></span>
          </div>
          <div class="heat-layer">
            <span v-for="i in 5" :key="'hw'+i" class="heat-wave" :style="{ animationDelay: (i * 0.35) + 's', left: (15 + i * 14) + '%' }"></span>
          </div>
        </div>
        <p class="anim-hint">🌪️ 循环热风中...</p>
      </div>

      <!-- 蒸锅动画 -->
      <div v-if="cookingMethod === 'steamer'" class="anim-steamer">
        <div class="steamer-scene">
          <span class="pot-emoji">♨️</span>
          <div class="steam-layer">
            <span v-for="i in 12" :key="'st'+i" class="steam-particle" :style="steamStyle(i)"></span>
          </div>
        </div>
        <p class="anim-hint">💨 蒸汽烹饪中...</p>
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

// 火焰粒子随机化
function flameStyle(i) {
  const left = 30 + (i % 6) * 8 + Math.random() * 4
  const delay = i * 0.12 + Math.random() * 0.2
  const hue = 15 + Math.random() * 25 // 橙红到金黄
  const size = 10 + Math.random() * 12
  return {
    left: left + '%',
    animationDelay: delay + 's',
    background: `linear-gradient(to top, hsl(${hue}, 90%, 50%), hsl(${hue + 15}, 100%, 60%), transparent)`,
    width: size + 'px',
    height: (size * 1.5 + 8) + 'px',
  }
}

// 蒸汽粒子随机化
function steamStyle(i) {
  const left = 15 + (i % 8) * 9 + Math.random() * 5
  const delay = i * 0.25 + Math.random() * 0.3
  const size = 6 + Math.random() * 10
  const drift = (Math.random() - 0.5) * 30
  return {
    left: left + '%',
    animationDelay: delay + 's',
    width: size + 'px',
    height: size + 'px',
    '--drift': drift + 'px',
  }
}
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
.nutrition-disclaimer {
  margin-top: 8px;
  padding: 8px 10px;
  background: rgba(217, 161, 91, 0.06);
  border-left: 3px solid var(--color-primary);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.nutrition-source {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-bottom: 2px;
}
.nutrition-warning {
  font-size: 11px;
  color: #b8860b;
  line-height: 1.4;
}
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
.animation-area { text-align: center; padding: 24px 0; position: relative; min-height: 160px; }

/* ===== 炒锅动画 ===== */
.wok-scene { position: relative; display: inline-flex; flex-direction: column; align-items: center; }
.wok-scene .pot-emoji { font-size: 48px; z-index: 2; }
.food-shake { position: absolute; top: -10px; display: flex; gap: 4px; z-index: 3; }
.food-piece {
  font-size: 16px;
  animation: foodBounce 0.6s ease-in-out infinite alternate;
}
@keyframes foodBounce {
  0% { transform: translateY(0) rotate(0deg); }
  100% { transform: translateY(-8px) rotate(15deg); }
}

.flame-layer { position: relative; width: 120px; height: 50px; margin-top: -8px; }
.flame-particle {
  position: absolute; bottom: 0;
  border-radius: 50% 50% 20% 20%;
  animation: flameDance 0.8s ease-in-out infinite alternate;
  transform-origin: center bottom;
}
@keyframes flameDance {
  0%   { transform: translateY(0) scale(1, 0.7) rotate(-3deg); opacity: 0.9; }
  40%  { transform: translateY(-18px) scale(0.7, 1.3) rotate(2deg); opacity: 0.7; }
  70%  { transform: translateY(-8px) scale(0.5, 1.1) rotate(-1deg); opacity: 0.5; }
  100% { transform: translateY(-24px) scale(0.3, 1.5) rotate(0deg); opacity: 0.2; }
}

/* ===== 空气炸锅动画 ===== */
.airfryer-scene { position: relative; display: inline-flex; flex-direction: column; align-items: center; }
.airfryer-scene .pot-emoji { font-size: 48px; z-index: 2; }

.air-circulation {
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 100px; height: 60px;
}
.air-dot {
  position: absolute;
  width: 4px; height: 4px;
  background: rgba(230, 126, 34, 0.6);
  border-radius: 50%;
  animation: airCirculate 1.8s linear infinite;
}
.air-dot:nth-child(odd) { background: rgba(241, 196, 15, 0.5); }
@keyframes airCirculate {
  0%   { transform: translate(0, 30px) scale(0.5); opacity: 0; }
  25%  { transform: translate(40px, 0) scale(1); opacity: 0.8; }
  50%  { transform: translate(0, -20px) scale(1.2); opacity: 1; }
  75%  { transform: translate(-40px, 0) scale(1); opacity: 0.8; }
  100% { transform: translate(0, 30px) scale(0.5); opacity: 0; }
}

.heat-layer { position: relative; width: 100px; height: 40px; margin-top: -6px; }
.heat-wave {
  position: absolute; bottom: 0;
  width: 3px; height: 28px;
  background: linear-gradient(to top, #e67e22, #f39c12, transparent);
  border-radius: 2px;
  animation: heatPulse 1.5s ease-out infinite;
}
@keyframes heatPulse {
  0%   { transform: translateY(5px) scaleY(0.3); opacity: 0.9; }
  50%  { transform: translateY(-15px) scaleY(1.2); opacity: 0.6; }
  100% { transform: translateY(-35px) scaleY(0.5); opacity: 0; }
}

/* ===== 蒸锅动画 ===== */
.steamer-scene { position: relative; display: inline-flex; flex-direction: column; align-items: center; }
.steamer-scene .pot-emoji { font-size: 48px; z-index: 2; }

.steam-layer { position: relative; width: 140px; height: 70px; margin-top: -10px; }
.steam-particle {
  position: absolute; bottom: 0;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: steamRise 2.5s ease-out infinite;
  filter: blur(1px);
}
@keyframes steamRise {
  0%   { transform: translateY(0) translateX(0) scale(0.3); opacity: 0.7; }
  30%  { transform: translateY(-20px) translateX(calc(var(--drift) * 0.5)) scale(1); opacity: 0.8; }
  60%  { transform: translateY(-45px) translateX(var(--drift)) scale(1.8); opacity: 0.4; }
  100% { transform: translateY(-70px) translateX(calc(var(--drift) * 1.5)) scale(2.5); opacity: 0; }
}

.anim-hint { font-size: var(--font-size-sm); color: var(--color-primary-dark); margin-top: 12px; font-weight: 500; }
.skip-btn { margin-top: 16px; font-size: 11px; }
</style>
