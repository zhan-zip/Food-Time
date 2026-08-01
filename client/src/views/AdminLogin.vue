<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">🔐 管理员登录</h1>
      <p class="auth-subtitle text-secondary">请输入管理员账号和密码</p>

      <form @submit.prevent="handleLogin" class="auth-form" novalidate>
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            :class="{ 'input--error': errors.email }"
            placeholder="请输入管理员邮箱"
            @input="clearError('email')"
          />
          <p v-if="errors.email" class="field-hint field-hint--error">{{ errors.email }}</p>
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="input"
            :class="{ 'input--error': errors.password }"
            placeholder="请输入密码"
            @input="clearError('password')"
          />
          <p v-if="errors.password" class="field-hint field-hint--error">{{ errors.password }}</p>
        </div>

        <p v-if="errorMsg" class="form-error">{{ errorMsg }}</p>

        <button type="submit" class="btn btn-primary btn-lg auth-submit" :disabled="loading">
          {{ loading ? '登录中...' : '登录管理后台' }}
        </button>
      </form>

      <p class="auth-footer text-sm">
        <router-link to="/" class="text-primary font-medium">返回首页</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const errorMsg = ref('')
const errors = reactive({ email: '', password: '' })
const form = reactive({ email: '', password: '' })

function clearError(field) {
  errors[field] = ''
  errorMsg.value = ''
}

function validate() {
  if (!form.email.trim()) {
    errors.email = '请输入邮箱地址'
    return false
  }
  if (!form.password) {
    errors.password = '请输入密码'
    return false
  }
  return true
}

async function handleLogin() {
  errorMsg.value = ''
  if (!validate()) return

  loading.value = true
  try {
    const res = await login(form.email, form.password)
    // 检查是否为管理员
    if (!res.user?.is_admin) {
      errorMsg.value = '该账号不是管理员，无法登录管理后台'
      return
    }

    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    router.push('/admin')
  } catch (e) {
    const detail = e?.response?.data?.detail
    // 修复 M11：拦截器已把错误转成 Error(message)，e.response 不存在 → 回退 e.message
    const msg = typeof detail === 'string' ? detail : (e?.message || '登录失败，请重试')
    errorMsg.value = msg
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, #1a1a2e15 0%, #16213e15 100%);
}
.auth-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
  border-top: 3px solid #e74c3c;
}
.auth-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  text-align: center;
  margin-bottom: 4px;
}
.auth-subtitle {
  text-align: center;
  margin-bottom: var(--spacing-xl);
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
.field-hint {
  font-size: 12px;
  margin-top: 4px;
  color: var(--color-text-muted);
  line-height: 1.4;
}
.field-hint--error {
  color: var(--color-danger);
}
.input--error {
  border-color: var(--color-danger);
}
.input--error:focus {
  box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.12);
}
.form-error {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
  background: rgba(220, 53, 69, 0.06);
  padding: 8px 12px;
  border-radius: var(--radius-sm);
}
.auth-submit {
  width: 100%;
  margin-top: var(--spacing-sm);
}
.auth-footer {
  text-align: center;
  margin-top: var(--spacing-lg);
}
@media (max-width: 640px) {
  .auth-card {
    padding: 28px 20px;
  }
}
</style>
