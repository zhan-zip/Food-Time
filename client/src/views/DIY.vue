<template>
  <div class="page container page-section">
    <h2 class="section-title">我的厨房</h2>

    <!-- 首次引导 -->
    <div v-if="showGuide" class="guide-banner" @click="showGuide = false">
      <span>👋 欢迎来到我的厨房！点击冰箱选择食材，然后让 AI 帮你烹饪</span>
      <button class="guide-close">&times;</button>
    </div>

    <!-- 桌面/平板布局：冰箱(3份) + 备菜盘(1份) -->
    <div class="diy-desktop">
      <div class="diy-fridge">
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

      <div class="diy-plate">
        <!-- 备菜盘 -->
        <PlateSection
          ref="plateRef"
          :items="store.plate"
          :max="store.MAX_PLATE"
          @remove="store.removeFromPlate"
          @clear="store.clearPlate"
        />
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
      </div>

      <!-- Tab: AI 烹饪助手（对话框面板，仅本 Tab 显示） -->
      <div v-show="mobileTab === 'ai'" class="mobile-panel">
        <AiPanel @publish-done="handlePublishFromDone" />
      </div>
    </div>

    <!-- 桌面端 AI 面板（≥769px 显示，移动端隐藏） -->
    <AiPanel class="desktop-ai" @publish-done="handlePublishFromDone" />

    <!-- 保存弹窗 -->
    <SaveDialog
      :visible="store.showSaveDialog"
      :default-name="store.aiSuggestion?.name || ''"
      :method-label="store.cookingMethods.find(m => m.key === store.cookingMethod)?.label || '炒锅'"
      :current-method="store.cookingMethod"
      :cooking-methods="store.cookingMethods"
      :saved-result="store.lastSavedRecipe"
      :save-error="saveError"
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
import AiPanel from '@/components/diy/AiPanel.vue'

const store = useDIYStore()
const plateRef = ref(null)
const saveError = ref('')

// 首次引导
const showGuide = ref(false)

// 移动端 Tab
const mobileTab = ref('fridge')
const mobileTabs = [
  { key: 'fridge', label: '食材区', icon: '🧊' },
  { key: 'plate', label: '备菜盘', icon: '🍽️' },
  { key: 'ai', label: 'AI 烹饪助手', icon: '🤖' },
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
/**
 * 飞行动画目标：
 * - 桌面布局：备菜盘（PlateSection 可见，width > 0）
 * - 移动端（备菜盘被 Tab 隐藏、尺寸为 0）→ 飞到「备菜盘」Tab 按钮
 */
function getFlyTarget() {
  const plateEl = plateRef.value?.$el || document.querySelector('.plate-section')
  if (plateEl && plateEl.getBoundingClientRect().width > 0) {
    return plateEl
  }
  const tabBtn = Array.from(document.querySelectorAll('.mobile-tab-btn')).find(
    (b) => b.innerText.includes('备菜盘')
  )
  return tabBtn || plateEl || null
}

function createFlyingCard(item, sourceEl) {
  if (!sourceEl) {
    console.debug('[Fly] sourceEl 为空，跳过飞行动画')
    return
  }
  // 飞行目标：桌面取备菜盘；移动端备菜盘不可见 → 飞到「备菜盘」Tab 按钮
  const target = getFlyTarget()
  if (!target) {
    console.debug('[Fly] 找不到飞行目标元素')
    return
  }

  const from = sourceEl.getBoundingClientRect()
  const to = target.getBoundingClientRect()

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
  saveError.value = ''
  const res = await store.doSave({ name, description, publishToSquare })
  if (res?.success === false) {
    saveError.value = res.message || '保存失败，请重试'
  }
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

/* AI 建议区：对话框式大面板 */
.ai-panel {
  margin-top: var(--spacing-lg);
  background: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.ai-panel-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--color-divider);
  background: linear-gradient(135deg, rgba(217, 161, 91, 0.10), rgba(217, 161, 91, 0.03));
}
.ai-head-avatar { font-size: 22px; line-height: 1; }
.ai-head-title { font-size: 15px; font-weight: 600; color: var(--color-text); }
.ai-head-tag {
  margin-left: auto;
  font-size: 11px;
  padding: 3px 12px;
  border-radius: 999px;
  background: rgba(217, 161, 91, 0.15);
  color: var(--color-primary-dark);
}
.ai-panel-body {
  padding: 28px 24px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.ai-welcome {
  text-align: center;
  color: var(--color-text-secondary);
}
.ai-welcome-icon { font-size: 44px; display: block; margin-bottom: 12px; }
.ai-welcome-text { font-size: 15px; line-height: 1.6; }

/* ==================== 桌面布局（≥769px，对齐全局 768 断点） ==================== */
@media (min-width: 769px) {
  .diy-desktop {
    display: grid;
    grid-template-columns: minmax(0, 3fr) minmax(240px, 1fr);
    gap: var(--spacing-lg);
    align-items: start;
  }
  .diy-fridge, .diy-plate {
    min-width: 0;
  }
  /* 备菜盘高度：上跟冰箱顶、下跟调料台底 */
  .diy-plate {
    align-self: stretch;
  }
  .diy-plate :deep(.plate-section) {
    height: 100%;
    display: flex;
    flex-direction: column;
    margin-bottom: 0;
  }
  .diy-plate :deep(.plate-area) {
    flex: 1;
    min-height: 220px;
  }
  .diy-plate :deep(.plate-items-inner) {
    align-content: flex-start;
  }
  .diy-mobile-tabs,
  .diy-mobile-content {
    display: none;
  }
}

/* ==================== 移动端/平板 Tab（≤768px） ==================== */
@media (max-width: 768px) {
  .diy-desktop {
    display: none;
  }
  .desktop-ai {
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

/* 769px 以上桌面 3fr:1fr；≤768px 移动端 Tab */
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
