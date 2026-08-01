<template>
  <div class="seasoning-rack">
    <h4 class="rack-label" :style="{ color: seasoning.color || '#95a5a6' }">
      {{ seasoning.label || '🧂 调料' }}
    </h4>
    <div class="rack-items">
      <IngredientCard
        v-for="item in seasoning.items"
        :key="'s_' + item.name"
        :name="item.name"
        :emoji="item.emoji || ''"
        :color="seasoning.color || '#95a5a6'"
        :selected="isSelected(item.name, 'seasoning')"
        @click="onSelect(item, 'seasoning', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import IngredientCard from './IngredientCard.vue'

const props = defineProps({
  seasoning: { type: Object, default: () => ({ key: 'seasoning', label: '🧂 调料', color: '#95a5a6', items: [] }) },
  selectedItems: { type: Array, default: () => [] },
})

const emit = defineEmits(['select'])

function onSelect(item, type, e) {
  emit('select', item, 'seasoning', type, e)
}

function isSelected(name, type) {
  return props.selectedItems.some(i => i.name === name && i.type === type)
}
</script>

<style scoped>
.seasoning-rack {
  padding: var(--spacing-sm) 0;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  margin: var(--spacing-sm) 0;
}
.rack-label {
  font-size: var(--font-size-xs);
  font-weight: 600;
  margin-bottom: 4px;
}
.rack-items {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.rack-items::-webkit-scrollbar {
  height: 4px;
}
.rack-items::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 2px;
}
</style>
