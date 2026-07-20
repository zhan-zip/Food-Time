<template>
  <div class="profile-page">
    <van-nav-bar title="我的" fixed />

    <div class="profile-content">
      <van-cell-group inset v-if="user">
        <van-cell :title="user.nickname" :label="user.email" center>
          <template #icon>
            <van-icon name="user-circle-o" size="40" style="margin-right: 12px" />
          </template>
        </van-cell>
      </van-cell-group>

      <van-cell-group inset style="margin-top: 12px">
        <van-cell title="管理后台" icon="setting-o" is-link @click="$router.push('/admin')" v-if="user?.is_admin" />
        <van-cell title="退出登录" icon="cross" title-style="color: #ee0a24" @click="handleLogout" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { getMe } from '../api/auth'

const router = useRouter()
const user = ref(null)

onMounted(async () => {
  try {
    user.value = await getMe()
  } catch {
    localStorage.removeItem('token')
    router.push('/login')
  }
})

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  showToast('已退出')
  router.push('/login')
}
</script>

<style scoped>
.profile-page {
  padding-top: 46px;
}
.profile-content {
  padding: 12px;
}
</style>
