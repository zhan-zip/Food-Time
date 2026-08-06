<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">注册</h1>
      <p class="auth-subtitle text-secondary">开启你的食光之旅</p>

      <form @submit.prevent="handleRegister" class="auth-form" novalidate>
        <!-- 头像（选填） -->
        <div class="form-group avatar-upload">
          <label class="form-label">头像</label>
          <div class="avatar-upload-row">
            <img :src="avatarPreview || '/static/default-avatar.png'" class="avatar-preview" alt="头像" />
            <div>
              <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="onAvatarChange" />
              <button type="button" class="btn btn-outline btn-sm" @click="avatarInput.click()">选择图片</button>
              <button v-if="avatarPreview" type="button" class="btn btn-outline btn-sm" @click="clearAvatar">移除</button>
              <p class="field-hint">选填，不上传则使用默认头像</p>
            </div>
          </div>
        </div>

        <!-- 昵称 -->
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input
            v-model="form.nickname"
            class="input"
            :class="{ 'input--error': errors.nickname }"
            placeholder="给自己起个名字"
            @input="clearError('nickname')"
          />
          <p v-if="errors.nickname" class="field-hint field-hint--error">{{ errors.nickname }}</p>
        </div>

        <!-- 邮箱 -->
        <div class="form-group">
          <label class="form-label">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            :class="{ 'input--error': errors.email }"
            placeholder="例如 example@qq.com"
            @input="clearError('email')"
          />
          <p v-if="errors.email" class="field-hint field-hint--error">{{ errors.email }}</p>
          <p v-else class="field-hint">用于接收验证码和找回密码</p>
        </div>

        <!-- 密码 -->
        <div class="form-group">
          <label class="form-label">密码</label>
          <input
            v-model="form.password"
            type="password"
            class="input"
            :class="{ 'input--error': errors.password }"
            placeholder="至少6位，包含字母和数字"
            @input="clearError('password')"
          />
          <p v-if="errors.password" class="field-hint field-hint--error">{{ errors.password }}</p>
          <p v-else class="field-hint">至少6位，建议包含字母和数字</p>
        </div>

        <!-- 验证码 -->
        <div class="form-group">
          <label class="form-label">验证码</label>
          <div class="code-row">
            <input
              v-model="form.code"
              class="input"
              :class="{ 'input--error': errors.code }"
              placeholder="输入邮箱中的6位验证码"
              @input="clearError('code')"
            />
            <button
              type="button"
              class="btn btn-outline btn-sm"
              @click="sendCode"
              :disabled="codeSending || countdown > 0"
            >
              {{ countdown > 0 ? `${countdown}秒后重发` : codeSending ? '发送中...' : '获取验证码' }}
            </button>
          </div>
          <p v-if="codeSent" class="field-hint field-hint--success">验证码已发送到 {{ form.email }}，请查收（检查垃圾箱）</p>
        </div>

        <!-- 选填：个人档案（用于个性化营养建议） -->
        <div class="form-group profile-optional">
          <label class="form-label">
            选填 · 个人档案
            <span class="text-xs text-muted">（用于个性化营养建议，可跳过）</span>
          </label>
          <div class="profile-fields">
            <select v-model="form.gender" class="input">
              <option value="">性别（选填）</option>
              <option value="male">男</option>
              <option value="female">女</option>
            </select>
            <input v-model="form.age" type="number" class="input" placeholder="年龄（选填）" min="1" max="120" />
            <input v-model="form.height_cm" type="number" class="input" placeholder="身高 cm（选填）" min="50" max="250" />
            <input v-model="form.weight_kg" type="number" class="input" placeholder="体重 kg（选填）" min="10" max="300" />
          </div>
          <p class="field-hint">不填则按成人通用标准推荐</p>
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
import request from '../api/request'

const router = useRouter()
const loading = ref(false)
const codeSending = ref(false)
const codeSent = ref(false)
const countdown = ref(0)
const errorMsg = ref('')
const errors = reactive({ nickname: '', email: '', password: '', code: '' })
const form = reactive({ email: '', password: '', nickname: '', code: '', avatar_url: '', age: '', gender: '', height_cm: '', weight_kg: '' })
const avatarPreview = ref('')
const avatarInput = ref(null)

function clearError(field) {
  errors[field] = ''
  errorMsg.value = ''
}

// ========== 前端校验 ==========
function validate() {
  // 昵称
  if (!form.nickname.trim()) {
    errors.nickname = '请输入昵称'
    return false
  }
  if (form.nickname.trim().length < 2) {
    errors.nickname = '昵称至少2个字'
    return false
  }

  // 邮箱
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email.trim()) {
    errors.email = '请输入邮箱地址'
    return false
  }
  if (!emailRe.test(form.email)) {
    errors.email = '邮箱格式不正确，例如 example@qq.com'
    return false
  }

  // 密码
  if (!form.password) {
    errors.password = '请输入密码'
    return false
  }
  if (form.password.length < 6) {
    errors.password = '密码至少6位'
    return false
  }
  if (!/[a-zA-Z]/.test(form.password) && !/\d/.test(form.password)) {
    // 纯符号/中文，提示
    errors.password = '密码需包含字母或数字'
    return false
  }

  // 验证码（可选，但后端校验时会检查）
  if (!form.code.trim()) {
    errors.code = '请输入验证码'
    return false
  }

  return true
}

// ========== 头像上传（压缩成正方形 base64，选填） ==========
function compressImage(file, maxSize = 256) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      const img = new Image()
      img.onload = () => {
        const side = Math.min(img.width, img.height)
        const canvas = document.createElement('canvas')
        canvas.width = maxSize
        canvas.height = maxSize
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, (img.width - side) / 2, (img.height - side) / 2, side, side, 0, 0, maxSize, maxSize)
        resolve(canvas.toDataURL('image/jpeg', 0.8))
      }
      img.onerror = reject
      img.src = e.target.result
    }
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function onAvatarChange(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) {
    alert('图片不能超过 5MB')
    if (avatarInput.value) avatarInput.value.value = ''
    return
  }
  try {
    const dataUrl = await compressImage(file)
    form.avatar_url = dataUrl
    avatarPreview.value = dataUrl
  } catch {
    alert('图片处理失败，请换一张')
  } finally {
    if (avatarInput.value) avatarInput.value.value = ''
  }
}

function clearAvatar() {
  form.avatar_url = ''
  avatarPreview.value = ''
  if (avatarInput.value) avatarInput.value.value = ''
}

// ========== 发送验证码 ==========
async function sendCode() {
  errorMsg.value = ''
  if (!form.email.trim()) {
    errors.email = '请先输入邮箱地址'
    return
  }
  const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRe.test(form.email)) {
    errors.email = '邮箱格式不正确'
    return
  }

  codeSending.value = true
  try {
    await request.post('/auth/send-code', { email: form.email })
    codeSent.value = true
    // 60 秒倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (e) {
    errorMsg.value = e.message || '发送失败'
  } finally {
    codeSending.value = false
  }
}

// ========== 注册 ==========
async function handleRegister() {
  errorMsg.value = ''
  if (!validate()) return

  loading.value = true
  try {
    const payload = {
      email: form.email,
      password: form.password,
      nickname: form.nickname,
      code: form.code,
      avatar_url: form.avatar_url || undefined,
      age: form.age ? Number(form.age) : undefined,
      gender: form.gender || undefined,
      height_cm: form.height_cm ? Number(form.height_cm) : undefined,
      weight_kg: form.weight_kg ? Number(form.weight_kg) : undefined,
    }
    const res = await request.post('/auth/register', payload)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    localStorage.setItem('onboard_pending', '1')  // 新用户标记：首页触发引导
    router.push('/')
  } catch (e) {
    errorMsg.value = e.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.avatar-upload-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}
.avatar-preview {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-primary);
  flex-shrink: 0;
}
.avatar-upload-row .btn + .btn {
  margin-left: var(--spacing-xs);
}
.profile-optional {
  border-top: 1px dashed var(--color-divider);
  padding-top: var(--spacing-md);
  margin-top: var(--spacing-lg);
}
.profile-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
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
.code-row {
  display: flex;
  gap: var(--spacing-sm);
}
.code-row .input { flex: 1; }
.code-row .btn { flex-shrink: 0; white-space: nowrap; }

/* 字段提示 */
.field-hint {
  font-size: 12px;
  margin-top: 4px;
  color: var(--color-text-muted);
  line-height: 1.4;
}
.field-hint--error {
  color: var(--color-danger);
}
.field-hint--success {
  color: var(--color-success);
}

/* 输入框错误状态 */
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
