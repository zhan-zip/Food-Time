<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">注册</h1>
      <p class="auth-subtitle text-secondary">开启你的食光之旅</p>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input v-model="form.nickname" class="input" placeholder="给自己起个名字" required />
        </div>

        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input v-model="form.email" type="email" class="input" placeholder="请输入邮箱" required />
        </div>

        <div class="form-group">
          <label class="form-label">密码</label>
          <input v-model="form.password" type="password" class="input" placeholder="至少6位密码" required minlength="6" />
        </div>

        <div class="form-group">
          <label class="form-label">验证码（开发模式留空即可）</label>
          <div class="code-row">
            <input v-model="form.code" class="input" placeholder="输入验证码" />
            <button type="button" class="btn btn-outline btn-sm" @click="sendCode" :disabled="codeSending">
              {{ codeSending ? '发送中' : '获取验证码' }}
            </button>
          </div>
        </div>

        <p v-if="errorMsg" class="form-error">{{ errorMsg }}</p>

        <button type="submit" class="btn btn-primary btn-lg auth-submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="auth-footer text-sm">
        已有账号？
        <router-link to="/login" class="text-primary font-medium">去登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const loading = ref(false)
const codeSending = ref(false)
const errorMsg = ref('')
const form = reactive({ email: '', password: '', nickname: '', code: '' })

async function sendCode() {
  if (!form.email) { errorMsg.value = '请先输入邮箱'; return }
  codeSending.value = true
  try {
    await axios.post('/api/auth/send-code', { email: form.email })
    alert('验证码已发送，开发模式下请查看后端控制台输出')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '发送失败'
  } finally {
    codeSending.value = false
  }
}

async function handleRegister() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await axios.post('/api/auth/register', form)
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    router.push('/')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '注册失败'
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
  max-width: 400px;
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
.code-row {
  display: flex;
  gap: var(--spacing-sm);
}
.form-error {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
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
