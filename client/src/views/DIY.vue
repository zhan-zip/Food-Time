<template>
  <div class="page container page-section">
    <h2 class="section-title">我的厨房</h2>

    <!-- 首次引导 -->
    <div v-if="showGuide" class="guide-banner" @click="showGuide = false">
      <span>👋 欢迎来到我的厨房！点击冰箱选择食材，然后让 AI 帮你烹饪</span>
      <button class="guide-close">&times;</button>
    </div>

    <!-- 桌面/平板布局 -->
    <div class="diy-desktop">
      <div class="diy-left">
        <!-- 备菜盘 -->
        <PlateSection
          ref="plateRef"
          :items="store.plate"
          :max="store.MAX_PLATE"
          @remove="store.removeFromPlate"
          @clear="store.clearPlate"
        />

        <!-- 烹饪面板（建议结果 + 动画） -->
        <CookingPanel
          :stage="store.stage"
          :can-suggest="store.canSuggest"
          :loading="store.stage === 'suggesting'"
          :ai-suggestion="store.aiSuggestion"
          :matched-recipes="store.matchedRecipes"
          :suggest-error="store.suggestError"
          :cooking-method="store.cookingMethod"
          :cooking-methods="store.cookingMethods"
          :show-animation="store.showAnimation"
          @suggest="store.fetchSuggestion()"
          @cook="store.startCooking()"
          @skip="store.skipAnimation()"
          @select-method="v => store.cookingMethod = v"
          @skip-animation="store.skipAnimation()"
        />

        <!-- 烹饪完成 → 保存提示 -->
        <div v-if="store.stage === 'saving' || store.stage === 'done'" class="card save-prompt">
          <template v-if="store.stage === 'saving'">
            <p class="text-sm">烹饪完成！要保存这道菜吗？</p>
            <button class="btn btn-primary" @click="store.openSaveDialog()">💾 保存菜谱</button>
          </template>
          <template v-else>
            <p class="text-sm" style="color:#52c41a">{{ store.lastSavedRecipe?.message || '菜谱已保存' }}</p>
            <div class="done-actions">
              <button class="btn btn-outline" @click="store.clearPlate()">🔄 再做一道</button>
              <button
                v-if="!store.lastSavedRecipe?.published"
                class="btn btn-primary"
                @click="handlePublishFromDone"
              >
                📤 发布到广场
              </button>
            </div>
          </template>
        </div>
      </div>

      <div class="diy-right">
        <!-- 冰箱 -->
        <FridgeSection
          :open="store.fridgeOpen"
          :left-categories="store.fridgeLeft"
          :right-categories="store.fridgeRight"
          :selected-items="store.plate"
          @open="store.fridgeOpen = true"
          @close="store.fridgeOpen = false"
          @select="(item, catKey, type, e) => onIngredientSelect(item, type, e)"
        />

        <!-- 已匹配提示 -->
        <div v-if="store.hasMatchedRecipes && store.stage !== 'selecting'" class="match-tip">
          📋 发现 {{ store.matchedRecipes.length }} 道相似菜谱
        </div>

        <!-- 调料台 -->
        <div v-if="store.seasoning?.items" style="margin-top: var(--spacing-md)">
          <SeasoningRack
            :seasoning="store.seasoning"
            :selected-items="store.plate"
            @select="(item, catKey, type, e) => onIngredientSelect(item, type, e)"
          />
        </div>
      </div>
    </div>

    <!-- 移动端底部 Tab -->
    <div class="diy-mobile-tabs">
      <button
        v-for="tab in mobileTabs"
        :key="tab.key"
        class="mobile-tab-btn"
        :class="{ active: mobileTab === tab.key }"
        @click="mobileTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </button>
    </div>

    <!-- 移动端 Tab 内容 -->
    <div class="diy-mobile-content">
      <!-- Tab: 冰箱 -->
      <div v-show="mobileTab === 'fridge'" class="mobile-panel">
        <FridgeSection
          :open="store.fridgeOpen"
          :left-categories="store.fridgeLeft"
          :right-categories="store.fridgeRight"
          :selected-items="store.plate"
          @open="store.fridgeOpen = true"
          @close="store.fridgeOpen = false"
          @select="(item, catKey, type, e) => onIngredientSelect(item, type, e)"
        />
        <SeasoningRack
          v-if="store.seasoning?.items"
          :seasoning="store.seasoning"
          :selected-items="store.plate"
          @select="(item, catKey, type, e) => onIngredientSelect(item, type, e)"
          style="margin-top: var(--spacing-md)"
        />
      </div>

      <!-- Tab: 备菜盘 -->
      <div v-show="mobileTab === 'plate'" class="mobile-panel">
        <PlateSection
          :items="store.plate"
          :max="store.MAX_PLATE"
          @remove="store.removeFromPlate"
          @clear="store.clearPlate"
        />
        <button
          v-if="store.canSuggest && store.plate.length > 0"
          class="btn btn-primary"
          style="width:100%"
          :disabled="store.stage === 'suggesting'"
          @click="store.fetchSuggestion()"
        >
          {{ store.stage === 'suggesting' ? 'AI 分析中...' : '🤖 获取 AI 烹饪建议' }}
        </button>
        <div v-if="store.hasMatchedRecipes && store.stage !== 'selecting'" class="match-tip" style="margin-top:8px">
          📋 发现 {{ store.matchedRecipes.length }} 道相似菜谱
        </div>
      </div>

      <!-- Tab: 烹饪 -->
      <div v-show="mobileTab === 'cooking'" class="mobile-panel">
        <CookingPanel
          :stage="store.stage"
          :can-suggest="store.canSuggest"
          :loading="store.stage === 'suggesting'"
          :ai-suggestion="store.aiSuggestion"
          :matched-recipes="store.matchedRecipes"
          :suggest-error="store.suggestError"
          :cooking-method="store.cookingMethod"
          :cooking-methods="store.cookingMethods"
          :show-animation="store.showAnimation"
          @suggest="store.fetchSuggestion()"
          @cook="store.startCooking()"
          @skip="store.skipAnimation()"
          @select-method="v => store.cookingMethod = v"
          @skip-animation="store.skipAnimation()"
        />
        <div v-if="store.stage === 'saving' || store.stage === 'done'" style="margin-top:12px; text-align:center">
          <template v-if="store.stage === 'saving'">
            <button class="btn btn-primary" @click="store.openSaveDialog()">💾 保存菜谱</button>
          </template>
          <template v-else>
            <p class="text-sm" style="color:#52c41a">{{ store.lastSavedRecipe?.message || '菜谱已保存' }}</p>
            <div class="done-actions" style="justify-content:center">
              <button class="btn btn-outline" @click="store.clearPlate()">🔄 再做一道</button>
              <button
                v-if="!store.lastSavedRecipe?.published"
                class="btn btn-primary"
                @click="handlePublishFromDone"
              >
                📤 发布到广场
              </button>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- 保存弹窗 -->
    <SaveDialog
      :visible="store.showSaveDialog"
      :default-name="store.aiSuggestion?.name || ''"
      :method-label="store.cookingMethods.find(m => m.key === store.cookingMethod)?.label || '炒锅'"
      :current-method="store.cookingMethod"
      :cooking-methods="store.cookingMethods"
      :saved-result="store.lastSavedRecipe"
      @cancel="store.showSaveDialog = false"
      @save="({ name, description, publishToSquare }) => handleSave(name, description, publishToSquare)"
      @publish="handlePublishFromDialog"
      @done="store.showSaveDialog = false; store.stage = 'done'"
      @update-method="v => store.cookingMethod = v"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useDIYStore } from '@/stores/diy'
import FridgeSection from '@/components/diy/FridgeSection.vue'
import PlateSection from '@/components/diy/PlateSection.vue'
import SeasoningRack from '@/components/diy/SeasoningRack.vue'
import CookingPanel from '@/components/diy/CookingPanel.vue'
import SaveDialog from '@/components/diy/SaveDialog.vue'

const store = useDIYStore()
const plateRef = ref(null)

// 首次引导
const showGuide = ref(false)

// 移动端 Tab
const mobileTab = ref('fridge')
const mobileTabs = [
  { key: 'fridge', label: '冰箱', icon: '🧊' },
  { key: 'plate', label: '备菜盘', icon: '🍽️' },
  { key: 'cooking', label: '烹饪', icon: '🍳' },
]

onMounted(async () => {
  await store.loadIngredients()
  if (store.plate.length === 0) {
    showGuide.value = true
  }
})

// ---------- 飞行动画 ----------
/**
 * 创建飞行克隆卡片：从 sourceEl 位置沿弧线飞到备菜盘
 * 动画阶段：拾取放大 → 弧线飞行 → 弹跳到达 → 淡出消失
 */
function createFlyingCard(item, sourceEl) {
  if (!sourceEl) {
    console.debug('[Fly] sourceEl 为空，跳过飞行动画')
    return
  }
  const plateEl = plateRef.value?.$el || document.querySelector('.plate-section')
  if (!plateEl) {
    console.debug('[Fly] 找不到备菜盘元素')
    return
  }

  const from = sourceEl.getBoundingClientRect()
  const to = plateEl.getBoundingClientRect()

  // 起点/终点中心坐标
  const sx = from.left + from.width / 2
  const sy = from.top + from.height / 2
  const tx = to.left + to.width / 2
  const ty = to.top + to.height / 2

  // 飞行卡片
  const card = document.createElement('div')
  card.className = 'diy-flying-card'
  card.innerHTML = `<span class="fc-emoji">${item.emoji || '📦'}</span><span class="fc-name">${item.name}</span>`
  Object.assign(card.style, {
    position: 'fixed',
    left: '0px',
    top: '0px',
    transform: `translate(${sx}px, ${sy}px) translate(-50%, -50%) scale(1)`,
    zIndex: '9999',
    pointerEvents: 'none',
    willChange: 'transform, opacity',
  })
  document.body.appendChild(card)

  console.debug('[Fly] 开始飞行:', item.name,
    `从(${Math.round(sx)},${Math.round(sy)}) 到(${Math.round(tx)},${Math.round(ty)})`)

  // ---- JS 动画循环：弧线飞行 ----
  const FLY_DURATION = 420 // 飞行总时长 ms
  const ARC_HEIGHT = Math.min(50, Math.abs(sy - ty) * 0.3 + 20) // 弧线高度

  const startTime = performance.now()

  function flyStep(now) {
    const elapsed = now - startTime
    const raw = Math.min(elapsed / FLY_DURATION, 1)

    // 缓出三次方，尾部减速明显
    const ease = 1 - Math.pow(1 - raw, 3)

    // 当前坐标（线性插值 × 缓出）
    const cx = sx + (tx - sx) * ease
    const cy = sy + (ty - sy) * ease

    // 弧线偏移：正弦曲线，中间点最高
    const arcY = -Math.sin(raw * Math.PI) * ARC_HEIGHT

    // 缩放：拾取时放大 → 飞行中缩小
    let scale
    if (raw < 0.12) {
      // 拾取阶段：1 → 1.12
      scale = 1 + (raw / 0.12) * 0.12
    } else {
      // 飞行缩小：1.12 → 0.65
      const flyRaw = (raw - 0.12) / 0.88
      scale = 1.12 - flyRaw * 0.47
    }

    card.style.transform = `translate(${cx}px, ${cy + arcY}px) translate(-50%, -50%) scale(${scale})`

    if (raw < 1) {
      requestAnimationFrame(flyStep)
    } else {
      // 飞行到达 → 弹跳淡出
      bounceOut(card)
    }
  }

  requestAnimationFrame(flyStep)
}

/** 到达弹跳 + 淡出移除 */
function bounceOut(card) {
  // 先弹一下
  card.style.transition = 'transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)'
  card.style.transform = card.style.transform.replace(/scale\([^)]+\)/, 'scale(0.8)')

  // 再缩回 + 淡出
  setTimeout(() => {
    card.style.transition = 'transform 0.2s ease-in, opacity 0.2s ease-in'
    card.style.transform = card.style.transform.replace(/scale\([^)]+\)/, 'scale(0.4)')
    card.style.opacity = '0'
  }, 200)

  // 移除 DOM
  setTimeout(() => {
    if (card.parentNode) card.parentNode.removeChild(card)
  }, 450)
}

/** 食材/调料选中：先飞行动画 → 飞行中段加入备菜盘（弹入动画） */
function onIngredientSelect(item, type, e) {
  if (store.plate.length >= store.MAX_PLATE) return

  // 找到被点击的源卡片元素
  let sourceEl = null
  if (e) {
    // e.target 可能是卡片内部的 span，用 closest 向上查找
    sourceEl = e.target?.closest?.('.ingredient-card')
    if (!sourceEl) {
      // 兜底：有些浏览器/环境下 currentTarget 可能指向绑定元素
      sourceEl = e.currentTarget?.closest?.('.ingredient-card') || e.currentTarget
    }
  }

  createFlyingCard(item, sourceEl)

  // 飞行完成（420ms）后加入备菜盘，触发弹入动画
  // 飞行卡片弹跳消失的同时，盘子卡片弹入出现
  const addDelay = sourceEl ? 350 : 0
  setTimeout(() => {
    store.addToPlate(item, type)
  }, addDelay)
}

async function handleSave(name, description, publishToSquare) {
  await store.doSave({ name, description, publishToSquare })
}

// 从弹窗中点击"发布到广场"
async function handlePublishFromDialog() {
  const res = await store.doPublishToSquare()
  if (res?.success) {
    store.lastSavedRecipe.message = res.message || '已提交审核'
  }
  store.showSaveDialog = false
  store.stage = 'done'
}

// 从 done 状态点击"发布到广场"
async function handlePublishFromDone() {
  const res = await store.doPublishToSquare()
  if (res?.success) {
    store.lastSavedRecipe.message = res.message || '已提交审核'
  }
}
</script>

<style scoped>
/* 引导横幅 */
.guide-banner {
  background: linear-gradient(135deg, rgba(217,161,91,0.15), rgba(217,161,91,0.06));
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-sm);
  cursor: pointer;
}
.guide-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--color-text-muted);
  padding: 0 4px;
}

/* 匹配提示 */
.match-tip {
  padding: 8px 12px;
  background: rgba(52, 152, 219, 0.08);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: #2980b9;
  margin-top: var(--spacing-sm);
}

/* 保存提示 */
.save-prompt {
  padding: var(--spacing-md);
  text-align: center;
  margin-top: var(--spacing-md);
}
.save-prompt .btn {
  margin-top: 8px;
}
.done-actions {
  display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; margin-top: 8px;
}

/* ==================== 桌面/平板布局 ==================== */
@media (min-width: 641px) {
  .diy-desktop {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
    align-items: start;
  }
  .diy-mobile-tabs,
  .diy-mobile-content {
    display: none;
  }
}

/* ==================== 移动端 Tab ==================== */
@media (max-width: 640px) {
  .diy-desktop {
    display: none;
  }
  .diy-mobile-tabs {
    display: flex;
    border-bottom: 1px solid var(--color-border);
    margin-bottom: var(--spacing-md);
    position: sticky;
    top: 56px;
    background: var(--color-bg);
    z-index: 10;
  }
  .mobile-tab-btn {
    flex: 1;
    padding: 10px 0;
    border: none;
    background: none;
    font-size: var(--font-size-sm);
    color: var(--color-text-muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: all 0.2s;
  }
  .mobile-tab-btn.active {
    color: var(--color-primary);
    border-bottom-color: var(--color-primary);
  }
  .diy-mobile-content {
    display: block;
  }
  .mobile-panel {
    padding: var(--spacing-sm) 0;
  }
}

/* ==================== 平板中等屏 ==================== */
@media (min-width: 641px) and (max-width: 900px) {
  .diy-desktop {
    grid-template-columns: 1fr;
  }
}
</style>

<!-- 飞行克隆卡片：全局样式（挂载到 document.body） -->
<style>
.diy-flying-card {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 68px;
  height: 78px;
  padding: 6px 4px;
  background: #fff;
  border: 1.5px solid var(--color-primary, #D9A15B);
  border-radius: 8px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.2), 0 2px 8px rgba(0, 0, 0, 0.08);
  font-size: 11px;
  white-space: nowrap;
  overflow: hidden;
}
.diy-flying-card .fc-emoji {
  font-size: 22px;
  line-height: 1;
}
.diy-flying-card .fc-name {
  font-size: 10px;
  color: #333;
  line-height: 1.2;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
</style>
