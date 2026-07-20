<template>
  <div class="register-page">
    <div class="register-header">
      <h1>注册账号</h1>
      <p>开始你的智能饮食之旅</p>
    </div>

    <van-form @submit="handleRegister" class="register-form">
      <van-cell-group inset>
        <van-field
          v-model="form.email"
          name="email"
          label="邮箱"
          placeholder="请输入邮箱"
          :rules="[{ required: true, message: '请输入邮箱' }]"
        />
        <van-field
          v-model="form.nickname"
          name="nickname"
          label="昵称"
          placeholder="给自己起个昵称（选填）"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="至少6位"
          :rules="[{ required: true, message: '请输入密码' }, { min: 6, message: '密码至少6位' }]"
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
          注册
        </van-button>
      </div>
    </van-form>

    <div class="register-footer">
      <van-button type="primary" size="small" @click="$router.push('/login')">
        已有账号？去登录
      </van-button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { register } from '../api/auth'

const router = useRouter()
const loading = ref(false)
const form = ref({ email: '', password: '', nickname: '' })

async function handleRegister() {
  loading.value = true
  try {
    const res = await register({
      email: form.value.email,
      password: form.value.password,
      nickname: form.value.nickname || undefined,
    })
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('user', JSON.stringify(res.user))
    showToast('注册成功')
    router.push('/home')
  } catch (e) {
    showToast(e.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #4CAF50 0%, #81C784 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
}
.register-header {
  text-align: center;
  color: #fff;
  margin-bottom: 40px;
}
.register-header h1 {
  font-size: 36px;
  margin: 0 0 8px;
}
.register-header p {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}
.register-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}
.register-footer {
  text-align: center;
  margin-top: 20px;
}
</style>
