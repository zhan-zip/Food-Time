<template>
  <button
    class="ingredient-card"
    :class="{ selected: selected }"
    :style="{ '--card-color': color }"
    @click="$emit('click', $event)"
  >
    <span class="card-emoji">{{ emoji }}</span>
    <span class="card-name">{{ name }}</span>
    <span class="card-bar" :style="{ background: color }"></span>
  </button>
</template>

<script setup>
defineProps({
  name: { type: String, required: true },
  emoji: { type: String, default: '' },
  color: { type: String, default: '#999' },
  selected: { type: Boolean, default: false },
})
defineEmits(['click'])
</script>

<style scoped>
.ingredient-card {
  width: 68px;
  height: 78px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 6px 4px;
  position: relative;
  overflow: hidden;
}
.ingredient-card:hover {
  border-color: var(--card-color, var(--color-primary));
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.ingredient-card.selected {
  border-color: var(--card-color, var(--color-primary));
  /* color-mix 兼容 fallback：旧浏览器不支持时以主色作为底色 */
  background: var(--color-primary);
  background: color-mix(in srgb, var(--card-color, #D9A15B) 8%, white);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--card-color, #D9A15B) 30%, transparent);
}
.card-emoji {
  font-size: 44px;  /* 食材 emoji 放大，作为卡片视觉主体 */
  line-height: 1;
}
.card-name {
  font-size: 10px;  /* 文字相应缩小，突出 emoji */
  color: var(--color-text);
  line-height: 1.2;
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
.card-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  border-radius: 0 0 var(--radius-md) var(--radius-md);
}
</style>
