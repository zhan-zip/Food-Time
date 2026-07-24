<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-overlay" @click.self="$emit('cancel')">
      <div class="dialog-card">
        <!-- 步骤 0：确认保存 -->
        <div v-if="step === 0">
          <h3 class="dialog-title">保存 DIY 菜谱？</h3>
          <p class="text-sm text-muted" style="margin-bottom:16px">
            将这道菜保存到你的个人菜谱中，方便以后查看。
          </p>
          <div class="dialog-actions">
            <button class="btn btn-outline" @click="$emit('cancel')">不保存</button>
            <button class="btn btn-primary" @click="step = 1">确认保存</button>
          </div>
        </div>

        <!-- 步骤 1：填写信息 -->
        <div v-if="step === 1">
          <h3 class="dialog-title">填写菜谱信息</h3>
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label class="form-label">菜名 <span style="color:#e74c3c">*</span></label>
              <input
                v-model="name"
                class="input"
                placeholder="给你的菜取个名字"
                required
                maxlength="100"
                autofocus
              />
            </div>
            <div class="form-group">
              <label class="form-label">简介</label>
              <textarea
                v-model="description"
                class="input"
                rows="2"
                placeholder="简单描述这道菜（可选）"
                maxlength="200"
              ></textarea>
            </div>
            <div class="form-group">
              <label class="form-label">烹饪方式</label>
              <select class="input" v-model="cookingMethod" @change="$emit('updateMethod', cookingMethod)">
                <option v-for="m in cookingMethods" :key="m.key" :value="m.key">{{ m.label }}</option>
              </select>
            </div>
            <div class="dialog-actions">
              <button type="button" class="btn btn-outline" @click="step = 0">上一步</button>
              <button type="submit" class="btn btn-primary" :disabled="!name.trim()">保存</button>
            </div>
          </form>
        </div>

        <!-- 步骤 2：是否发布 -->
        <div v-if="step === 2">
          <h3 class="dialog-title">保存成功！</h3>
          <p class="text-sm" style="color:#52c41a; margin-bottom:16px">{{ savedResult?.message || '菜谱已保存' }}</p>
          <p class="text-sm text-muted" style="margin-bottom:16px">是否同时发布到美食广场，让更多人看到你的作品？</p>
          <div class="dialog-actions">
            <button class="btn btn-outline" @click="$emit('done')">仅保存</button>
            <button class="btn btn-primary" @click="$emit('publish')">发布到广场</button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  defaultName: { type: String, default: '' },
  methodLabel: { type: String, default: '炒锅' },
  savedResult: { type: Object, default: null },
  cookingMethods: { type: Array, default: () => [
    { key: 'wok', label: '炒锅' },
    { key: 'air_fryer', label: '空气炸锅' },
    { key: 'steamer', label: '蒸锅' },
  ]},
  currentMethod: { type: String, default: 'wok' },
})

const emit = defineEmits(['cancel', 'save', 'publish', 'done', 'updateMethod'])

const step = ref(0)
const name = ref('')
const description = ref('')
const cookingMethod = ref(props.currentMethod)

// 重置
watch(() => props.visible, (v) => {
  if (v) {
    step.value = 0
    name.value = props.defaultName || ''
    description.value = ''
    cookingMethod.value = props.currentMethod
  }
})

function handleSubmit() {
  if (!name.value.trim()) return
  emit('save', { name: name.value.trim(), description: description.value.trim(), publishToSquare: false })
  step.value = 2
}
</script>

<style scoped>
.dialog-overlay {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.dialog-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  width: 90%; max-width: 420px;
  box-shadow: var(--shadow-lg);
  animation: slideUp 0.3s ease-out;
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.dialog-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}
.dialog-actions {
  display: flex; gap: 8px; justify-content: flex-end;
}
.dialog-actions .btn { min-width: 100px; }
.form-group {
  margin-bottom: var(--spacing-md);
}
</style>
