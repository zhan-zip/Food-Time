<template>
  <div id="app-container">
    <!-- 无 TabBar 的页面（登录/注册等） -->
    <router-view v-if="!showTabbar" />

    <!-- 有 TabBar 的主页面 -->
    <template v-else>
      <div class="main-content">
        <router-view />
      </div>
      <van-tabbar v-model="active" route placeholder>
        <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
        <van-tabbar-item icon="search" to="/food">食物</van-tabbar-item>
        <van-tabbar-item icon="chat-o" to="/chat">AI</van-tabbar-item>
        <van-tabbar-item icon="balance-o" to="/expense">记账</van-tabbar-item>
        <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
      </van-tabbar>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const showTabbar = computed(() => {
  const noTabRoutes = ['Login', 'Register', 'Admin']
  return !noTabRoutes.includes(route.name)
})
</script>

<style>
#app-container {
  min-height: 100vh;
  background: #f7f8fa;
}
.main-content {
  padding-bottom: 50px;
}
</style>
