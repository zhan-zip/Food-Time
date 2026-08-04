<template>
  <div class="ai-panel">
    <div class="ai-panel-head">
      <span class="ai-head-avatar">🤖</span>
      <span class="ai-head-title">AI 烹饪助手</span>
      <span class="ai-head-tag">食材建议</span>
    </div>
    <div class="ai-panel-body">
      <!-- 空备菜盘引导 -->
      <div v-if="store.plate.length === 0" class="ai-welcome">
        <span class="ai-welcome-icon">🍽️</span>
        <p class="ai-welcome-text">您的备菜盘是空的哦，试着加入食材吧</p>
      </div>

      <!-- 有食材 → 烹饪面板（建议结果 + 动画） -->
      <CookingPanel
        v-else
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
              @click="$emit('publish-done')"
            >
              📤 发布到广场
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDIYStore } from '@/stores/diy'
import CookingPanel from './CookingPanel.vue'

const store = useDIYStore()
defineEmits(['publish-done'])
</script>

<style scoped>
.ai-panel {
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
</style>
