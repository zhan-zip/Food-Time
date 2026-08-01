<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">登录</h1>
      <p class="auth-subtitle text-secondary">欢迎回到食光记</p>

      <form @submit.prevent="handleLogin" class="auth-form" novalidate>
        <!-- 邮箱 -->
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            :class="{ 'input--error': errors.email }"
            placeholder="请输入邮箱"
            @input="clearError('email')"
          />
          <p v-if="errors.email" class="field-hint field-hint--error">{{ errors.email }}</p>
        </div>

        <!-- 密码 -->
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
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="auth-footer text-sm">
        还没有账号？
        <router-link to="/register" class="text-primary font-medium">立即注册</router-link>
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
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRe.test(form.email)) {
    errors.email = '邮箱格式不正确，例如 example@qq.com'
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
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    router.push('/')
  } catch (e) {
    errorMsg.value = e.message || '登录失败，请重试'  // 修复 M11：拦截器已转为 Error(message)，e.response 不存在
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
  background: linear-gradient(135deg, #D9A15B15 0%, #D8B08C15 100%);
}
.auth-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
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
