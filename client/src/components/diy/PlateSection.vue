<template>
  <div class="plate-section">
    <!-- 盘中食材 -->
    <div class="plate-area" :class="{ 'has-items': items.length > 0 }">
      <div v-if="items.length === 0" class="plate-empty">
        <span class="plate-icon">🍽️</span>
        <p class="text-muted text-sm">从冰箱和调料台选择食材<br/>放入备菜盘</p>
      </div>
      <div v-else class="plate-items">
        <div class="plate-items-inner">
          <button
            v-for="(item, idx) in items"
            :key="item.name + item.type"
            class="plate-item"
            :class="{ 'fly-in': item._animating }"
            @click="$emit('remove', idx)"
            :title="'点击移除 ' + item.name"
          >
            <span class="pi-emoji">{{ item.emoji || '📦' }}</span>
            <span class="pi-name">{{ item.name }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 计数 + 上限 -->
    <div v-if="items.length > 0" class="plate-info">
      <span class="text-xs text-muted">{{ items.length }} / {{ max }} 种食材</span>
      <button class="link-btn text-xs" @click="$emit('clear')">清空</button>
    </div>
  </div>
</template>

<script setup>
import { watch, onBeforeUnmount } from 'vue'

const props = defineProps({
  items: { type: Array, default: () => [] },
  max: { type: Number, default: 12 },
})
const emit = defineEmits(['remove', 'clear'])

// 手动飞入动画：watch items 长度变化，给新增项加 _animating 标记
let lastLength = 0
const animTimers = []
watch(() => props.items.length, (newLen) => {
  if (newLen > lastLength) {
    // 新增的项在尾部，标记动画
    for (let i = lastLength; i < newLen; i++) {
      const item = props.items[i]
      item._animating = true
      animTimers.push(setTimeout(() => { item._animating = false }, 500))
    }
  }
  lastLength = newLen
})
// 卸载时清理动画标记定时器，避免组件销毁后仍触发 DOM 更新
onBeforeUnmount(() => {
  animTimers.forEach(clearTimeout)
  animTimers.length = 0
})
</script>

<style scoped>
.plate-section {
  margin-bottom: var(--spacing-md);
}
.plate-area {
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  transition: all 0.3s ease;
}
.plate-area.has-items {
  border-color: var(--color-primary);
  border-style: solid;
  background: rgba(217, 161, 91, 0.03);
}
.plate-empty {
  text-align: center;
}
.plate-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 8px;
}
.plate-items {
  /* wrapper */
}
.plate-items-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
}
.plate-item {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 6px 10px;
  background: var(--color-bg-card);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: var(--font-size-xs);
}
.plate-item:hover {
  border-color: #e74c3c;
  background: rgba(231, 76, 60, 0.06);
}
.pi-emoji {
  font-size: 18px;
}
.pi-name {
  font-size: 10px;
  color: var(--color-text);
}
.plate-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 6px;
  padding: 0 4px;
}
.link-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  padding: 0;
}

</style>

<!-- 弹入动画 -->
<style>
.fly-in {
  animation: plateFlyIn 0.45s cubic-bezier(0.34, 1.56, 0.64, 1);
  will-change: transform, opacity;
}
@keyframes plateFlyIn {
  0%   { transform: translateY(-40px) scale(0.3); opacity: 0; }
  50%  { transform: translateY(8px) scale(1.08); opacity: 1; }
  70%  { transform: translateY(-4px) scale(0.94); }
  85%  { transform: translateY(2px) scale(1.02); }
  100% { transform: translateY(0) scale(1); opacity: 1; }
}
</style>
