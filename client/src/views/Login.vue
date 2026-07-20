<template>
  <div class="login-page">
    <div class="login-header">
      <h1>Food-Time</h1>
      <p>智能饮食助手</p>
    </div>

    <van-form @submit="handleLogin" class="login-form">
      <van-cell-group inset>
        <van-field
          v-model="form.email"
          name="email"
          label="邮箱"
          placeholder="请输入邮箱"
          :rules="[{ required: true, message: '请输入邮箱' }]"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
        />
      </van-cell-group>

      <div style="margin: 16px">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          :loading="loading"
        >
          登录
        </van-button>
      </div>
    </van-form>

    <div class="login-footer">
      <van-button type="primary" size="small" @click="$router.push('/register')">
        没有账号？去注册
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { login } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const form = ref({ email: '', password: '' })

async function handleLogin() {
  loading.value = true
  try {
    const res = await login(form.value)
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    showToast('登录成功')
    router.push('/home')
  } catch (e) {
    showToast(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
}
.login-header {
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}
.login-header h1 {
  font-size: 36px;
  margin: 0 0 8px;
}
.login-header p {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}
.login-footer {
  text-align: center;
  margin-top: 20px;
}
</style>
