<template>
  <div class="admin-page">
    <van-nav-bar title="管理后台" fixed left-text="返回" @click-left="$router.back()" />

    <div class="admin-content">
      <van-cell-group title="数据统计" inset>
        <van-cell title="用户数" :value="String(stats.users)" />
        <van-cell title="食物数" :value="String(stats.foods)" />
        <van-cell title="食谱数" :value="String(stats.recipes)" />
      </van-cell-group>

      <van-cell-group title="管理功能" inset style="margin-top: 12px">
        <van-cell title="用户管理" is-link @click="showToast('P2 实现')" />
        <van-cell title="食谱审核" is-link @click="showToast('P2 实现')" />
      </van-cell-group>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import request from '../api/request'

const stats = ref({ users: 0, foods: 0, recipes: 0 })

onMounted(async () => {
  try {
    const res = await request.get('/admin/stats')
    stats.value = res
  } catch { /* ignored */ }
})
</script>

<style scoped>
.admin-page {
  padding-top: 46px;
}
.admin-content {
  padding: 12px;
}
</style>
