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

      <!-- 忘记密码弹窗 -->
      <div v-if="showForgot" class="modal-overlay" @click.self="closeForgot">
        <div class="modal-content card">
          <h3 style="margin-bottom:4px">忘记密码</h3>
          <p class="text-xs text-muted" style="margin-bottom:12px">通过邮箱验证码重置密码</p>
          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input v-model="forgot.email" type="email" class="input" placeholder="请输入注册邮箱" />
          </div>
          <div class="form-group">
            <label class="form-label">验证码</label>
            <div class="code-row">
              <input v-model="forgot.code" class="input" placeholder="6位验证码" />
              <button class="btn btn-outline btn-sm" @click="sendForgotCode" :disabled="forgotSending || forgotCountdown > 0">
                {{ forgotCountdown > 0 ? `${forgotCountdown}秒后重发` : forgotSending ? '发送中...' : '获取验证码' }}
              </button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input v-model="forgot.newPassword" type="password" class="input" placeholder="至少6位，包含字母或数字" />
          </div>
          <p v-if="forgotMsg" class="text-sm" :style="{ color: forgotOk ? '#52c41a' : '#e74c3c', marginBottom: '8px' }">{{ forgotMsg }}</p>
          <div class="modal-actions">
            <button class="btn btn-outline" @click="closeForgot">取消</button>
            <button class="btn btn-primary" @click="handleReset" :disabled="forgotLoading">{{ forgotLoading ? '重置中...' : '重置密码' }}</button>
          </div>
        </div>
      </div>

      <p class="auth-footer text-sm">
        还没有账号？
        <router-link to="/register" class="text-primary font-medium">立即注册</router-link>
        <span class="auth-divider">|</span>
        <a href="#" class="text-primary font-medium" @click.prevent="showForgot = true">忘记密码？</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login, forgotPassword, resetPassword } from '../api/auth'

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

// ========== 忘记密码（重置密码） ==========
const showForgot = ref(false)
const forgot = reactive({ email: '', code: '', newPassword: '' })
const forgotSending = ref(false)
const forgotLoading = ref(false)
const forgotCountdown = ref(0)
const forgotMsg = ref('')
const forgotOk = ref(false)

function closeForgot() {
  showForgot.value = false
  forgotMsg.value = ''
  forgot.email = ''
  forgot.code = ''
  forgot.newPassword = ''
}

async function sendForgotCode() {
  if (!forgot.email.trim()) return alert('请输入邮箱')
  forgotSending.value = true
  forgotMsg.value = ''
  try {
    await forgotPassword(forgot.email)
    forgotMsg.value = '验证码已发送到邮箱'
    forgotOk.value = true
    forgotCountdown.value = 60
    const t = setInterval(() => {
      forgotCountdown.value--
      if (forgotCountdown.value <= 0) clearInterval(t)
    }, 1000)
  } catch (e) {
    forgotMsg.value = e.message || '发送失败'
    forgotOk.value = false
  } finally {
    forgotSending.value = false
  }
}

async function handleReset() {
  if (!forgot.email.trim() || !forgot.code.trim() || !forgot.newPassword) return alert('请填写完整信息')
  if (forgot.newPassword.length < 6) return alert('新密码至少 6 位')
  forgotLoading.value = true
  forgotMsg.value = ''
  try {
    await resetPassword({ email: forgot.email, code: forgot.code, new_password: forgot.newPassword })
    forgotMsg.value = '密码已重置，请用新密码登录'
    forgotOk.value = true
    setTimeout(closeForgot, 1500)
  } catch (e) {
    forgotMsg.value = e.message || '重置失败'
    forgotOk.value = false
  } finally {
    forgotLoading.value = false
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
.auth-divider {
  margin: 0 var(--spacing-xs);
  color: var(--color-text-muted);
}
/* 忘记密码弹窗 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  width: 400px;
  max-width: 90vw;
  padding: var(--spacing-lg);
}
.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}
.code-row {
  display: flex;
  gap: var(--spacing-sm);
}
.code-row .input { flex: 1; }
.code-row .btn { flex-shrink: 0; white-space: nowrap; }
@media (max-width: 640px) {
  .auth-card {
    padding: 28px 20px;
  }
}
</style>
