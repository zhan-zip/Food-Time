<template>
  <div class="page container page-section">
    <h2 class="section-title">记账</h2>

    <div class="expense-layout">
      <!-- 录入表单 -->
      <div class="card">
        <h3>&#x1F4DD; 手动录入</h3>
        <div class="form-group">
          <label class="form-label">金额</label>
          <input v-model="form.amount" type="number" step="0.01" class="input" placeholder="0.00" />
        </div>
        <div class="form-group">
          <label class="form-label">分类</label>
          <select v-model="form.category" class="input">
            <option value="">选择分类</option>
            <option value="餐饮">餐饮</option>
            <option value="购物">购物</option>
            <option value="交通">交通</option>
            <option value="娱乐">娱乐</option>
            <option value="其他">其他</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">备注</label>
          <input v-model="form.note" class="input" placeholder="备注（可选）" />
        </div>
        <button class="btn btn-primary" @click="submitExpense">记录</button>
      </div>

      <!-- OCR 识图 -->
      <div class="card">
        <h3>&#x1F4F7; 拍照识别</h3>
        <div class="ocr-upload">
          <span>&#x1F4F7;</span>
          <p class="text-sm text-muted">上传账单/小票图片，AI 自动识别金额和商户</p>
          <input type="file" accept="image/*" class="ocr-input" disabled />
          <p class="text-xs text-muted">OCR 功能将在 P1 阶段接入 Qwen VL</p>
        </div>
      </div>
    </div>

    <!-- 统计图 -->
    <div class="card" style="margin-top: var(--spacing-lg);">
      <h3>&#x1F4CA; 消费统计</h3>
      <p class="text-muted text-sm">统计图表将在 P1 阶段实现。届时将以饼图和折线图展示消费分布和趋势。</p>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const form = reactive({ amount: '', category: '', note: '' })

function submitExpense() {
  if (!form.amount || !form.category) {
    alert('请填写金额和分类')
    return
  }
  alert('记账功能将在 P1 阶段实现数据持久化存储')
  form.amount = ''
  form.note = ''
}
</script>

<style scoped>
.expense-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
}
.form-group {
  margin-bottom: var(--spacing-md);
}
.form-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 500;
  margin-bottom: var(--spacing-xs);
  color: var(--color-text-secondary);
}
.ocr-upload {
  text-align: center;
  padding: 32px var(--spacing-lg);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-md);
}
.ocr-upload span {
  font-size: 36px;
  display: block;
  margin-bottom: var(--spacing-sm);
}
.ocr-input {
  margin-top: var(--spacing-md);
}
@media (max-width: 640px) {
  .expense-layout {
    grid-template-columns: 1fr;
  }
}
</style>
