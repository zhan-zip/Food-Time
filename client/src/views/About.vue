<template>
  <div class="page container page-section">
    <h2 class="section-title">关于我</h2>

    <div class="profile-card card">
      <div class="profile-header">
        <span class="profile-avatar">&#x1F464;</span>
        <div>
          <h2>{{ user?.nickname || '未登录' }}</h2>
          <p class="text-sm text-secondary">{{ user?.email }}</p>
        </div>
      </div>
    </div>

    <!-- 饮食偏好 -->
    <div class="card" style="margin-top: var(--spacing-md);">
      <h3 class="card-title">&#x1F4CA; 饮食偏好分析</h3>
      <p class="text-muted text-sm">功能将在 P2 阶段实现。届时将自动分析你的口味偏好、菜系偏好等。</p>
    </div>

    <!-- 营养分析 -->
    <div class="card" style="margin-top: var(--spacing-md);">
      <h3 class="card-title">&#x1F4C8; 营养分析</h3>
      <p class="text-muted text-sm">功能将在 P2 阶段实现。届时将以雷达图和柱状图展示 7/30 天营养摄入。</p>
    </div>

    <!-- 退出 -->
    <div style="margin-top: var(--spacing-xl);">
      <button class="btn btn-outline" style="color: var(--color-danger); border-color: var(--color-danger);" @click="handleLogout">
        退出登录
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)

onMounted(() => {
  try {
    user.value = JSON.parse(localStorage.getItem('user'))
  } catch { /* ignore */ }
})

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/login')
}
</script>

<style scoped>
.profile-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}
.profile-avatar {
  font-size: 48px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-warm);
  border-radius: 50%;
}
.card-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}
</style>
