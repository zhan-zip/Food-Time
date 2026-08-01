<template>
  <div class="fridge-outer" ref="fridgeOuter">
    <!-- 关闭状态 -->
    <div v-if="!open" class="fridge-closed" @click="$emit('open')">
      <span class="fridge-icon">🧊</span>
      <span class="fridge-hint">点击打开冰箱</span>
    </div>

    <!-- 打开状态：双门 -->
    <div v-else class="fridge-open">
      <!-- 左门阴影/背板 -->
      <div class="fridge-door fridge-door-left">
        <div class="door-inner-wrapper">
          <div
            v-for="cat in leftCategories"
            :key="cat.key"
            class="fridge-section"
          >
            <h4 class="section-label" :style="{ color: cat.color }">{{ cat.label }}</h4>
            <div class="section-items">
              <IngredientCard
                v-for="item in cat.items"
                :key="cat.key + item.name"
                :name="item.name"
                :emoji="item.emoji || ''"
                :color="cat.color"
                :selected="isSelected(item.name, 'ingredient')"
                @click="onSelectItem(item, cat.key, 'ingredient', $event)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 右门阴影/背板 -->
      <div class="fridge-door fridge-door-right">
        <div class="door-inner-wrapper">
          <div
            v-for="cat in rightCategories"
            :key="cat.key"
            class="fridge-section"
          >
            <h4 class="section-label" :style="{ color: cat.color }">{{ cat.label }}</h4>
            <div class="section-items">
              <IngredientCard
                v-for="item in cat.items"
                :key="cat.key + item.name"
                :name="item.name"
                :emoji="item.emoji || ''"
                :color="cat.color"
                :selected="isSelected(item.name, 'ingredient')"
                @click="onSelectItem(item, cat.key, 'ingredient', $event)"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import IngredientCard from './IngredientCard.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  leftCategories: { type: Array, default: () => [] },
  rightCategories: { type: Array, default: () => [] },
  selectedItems: { type: Array, default: () => [] },
})

const emit = defineEmits(['open', 'select', 'close'])
const fridgeOuter = ref(null)

function isSelected(name, type) {
  return props.selectedItems.some(i => i.name === name && i.type === type)
}

function onSelectItem(item, catKey, type, e) {
  emit('select', item, catKey, type, e)
}

// 点击外部关闭冰箱（排除交互控件——调料、按钮等）
function onClickOutside(e) {
  if (!props.open || !fridgeOuter.value) return
  // 忽略点击在冰箱内部
  if (fridgeOuter.value.contains(e.target)) return
  // 忽略点击在交互控件上（食材卡片、按钮、弹窗等）
  if (e.target.closest('.ingredient-card, .btn, .dialog-overlay, .plate-section')) return
  emit('close')
}

onMounted(() => {
  // 用 pointerdown（比 click 早），确保 Vue 重渲染前完成 contains 检测
  document.addEventListener('pointerdown', onClickOutside)
})
onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onClickOutside)
})
</script>

<style scoped>
.fridge-outer {
  perspective: 1200px;
  width: 100%;
}
.fridge-closed {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 160px;
}
.fridge-closed:hover {
  border-color: var(--color-primary);
  background: rgba(217, 161, 91, 0.04);
}
.fridge-icon {
  font-size: 48px;
  margin-bottom: 8px;
}
.fridge-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

/* 打开态 */
.fridge-open {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  animation: fridgeReveal 0.5s ease-out;
}
@keyframes fridgeReveal {
  0% { opacity: 0; transform: scaleY(0.95); }
  100% { opacity: 1; transform: scaleY(1); }
}

.fridge-door {
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-sm);
  background: var(--color-bg-card);
  max-height: 360px;
  overflow-y: auto;
  animation: doorOpen 0.45s ease-out;
}
.fridge-door-left {
  transform-origin: left center;
  animation: doorOpenLeft 0.45s ease-out;
}
.fridge-door-right {
  transform-origin: right center;
  animation: doorOpenRight 0.45s ease-out;
}
@keyframes doorOpenLeft {
  0% { transform: rotateY(90deg); opacity: 0; }
  100% { transform: rotateY(0deg); opacity: 1; }
}
@keyframes doorOpenRight {
  0% { transform: rotateY(-90deg); opacity: 0; }
  100% { transform: rotateY(0deg); opacity: 1; }
}

.door-inner-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.fridge-section {
  /* category group */
}
.section-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  margin-bottom: 4px;
}
.section-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
