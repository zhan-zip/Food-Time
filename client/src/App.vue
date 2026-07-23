<template>
  <div id="app-container">
    <!-- 无导航的页面（登录/注册等） -->
    <router-view v-if="!showNav" />

    <!-- 有导航的主页面 -->
    <div v-else class="app-layout">
      <!-- 桌面端：左侧导航栏 -->
      <nav class="desktop-sidebar">
        <div class="sidebar-logo">
          <span class="logo-icon">🍽️</span>
          <span class="logo-text">Food-Time</span>
        </div>
        <div class="sidebar-menu">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="sidebar-item"
            active-class="sidebar-item--active"
          >
            <span class="sidebar-icon">{{ item.emoji }}</span>
            <span class="sidebar-label">{{ item.label }}</span>
          </router-link>
        </div>
        <div class="sidebar-footer">
          <span>智能饮食助手 v0.1</span>
        </div>
      </nav>

      <!-- 主内容区 -->
      <main class="main-area">
        <router-view />
      </main>

      <!-- 移动端：底部 TabBar -->
      <van-tabbar route placeholder class="mobile-tabbar">
        <van-tabbar-item
          v-for="item in navItems"
          :key="item.to"
          :icon="item.icon"
          :to="item.to"
        >
          {{ item.label }}
        </van-tabbar-item>
      </van-tabbar>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const showNav = computed(() => {
  const noNavRoutes = ['Login', 'Register', 'Admin']
  return !noNavRoutes.includes(route.name)
})

const navItems = [
  { to: '/home',    label: '首页', icon: 'home-o',    emoji: '🏠' },
  { to: '/food',    label: '食物', icon: 'search',    emoji: '🍜' },
  { to: '/chat',    label: 'AI',   icon: 'chat-o',    emoji: '🤖' },
  { to: '/expense', label: '记账', icon: 'balance-o', emoji: '💰' },
  { to: '/profile', label: '我的', icon: 'user-o',    emoji: '👤' },
]
</script>

<style>
/* ===== 基础布局 ===== */
#app-container {
  min-height: 100vh;
  background: #f7f8fa;
}

.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ===== 桌面端侧边栏 ===== */
.desktop-sidebar {
  display: none;             /* 移动端隐藏 */
  width: 220px;
  min-width: 220px;
  background: #fff;
  border-right: 1px solid #ebedf0;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 10;
}

.sidebar-logo {
  padding: 24px 20px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #ebedf0;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #333;
}

.sidebar-menu {
  flex: 1;
  padding: 12px 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin: 2px 8px;
  border-radius: 8px;
  color: #555;
  font-size: 15px;
  text-decoration: none;
  transition: all 0.2s;
}

.sidebar-item:hover {
  background: #f0fdf4;
  color: #4CAF50;
}

.sidebar-item--active {
  background: #e8f5e9;
  color: #4CAF50;
  font-weight: 600;
}

.sidebar-icon {
  font-size: 20px;
  width: 28px;
  text-align: center;
}

.sidebar-footer {
  padding: 16px 20px;
  font-size: 12px;
  color: #bbb;
  border-top: 1px solid #ebedf0;
}

/* ===== 主内容区 ===== */
.main-area {
  flex: 1;
  max-width: 960px;
  margin: 0 auto;
  padding: 24px 20px;
  width: 100%;
  min-height: 100vh;
}

/* ===== 移动端底部 TabBar（默认显示） ===== */
.mobile-tabbar {
  display: flex;
}

/* ===== 响应式断点 ===== */

/* 桌面端（≥768px）：显示侧边栏，隐藏底部 TabBar */
@media (min-width: 768px) {
  .desktop-sidebar {
    display: flex;
  }

  .mobile-tabbar {
    display: none;
  }

  .main-area {
    padding: 32px;
    padding-bottom: 32px;
  }
}

/* 移动端（<768px）：底部预留 TabBar 高度 */
@media (max-width: 767px) {
  .main-area {
    padding: 16px 14px;
    padding-bottom: 60px;  /* 给 TabBar 让位 */
    max-width: 100%;
  }
}

/* ===== Vant TabBar 主题色覆盖 ===== */
.van-tabbar-item--active {
  color: #4CAF50;
}

/* ===== 路由过渡动画 ===== */
.main-area .router-view-enter-active,
.main-area .router-view-leave-active {
  transition: opacity 0.2s ease;
}
.main-area .router-view-enter-from,
.main-area .router-view-leave-to {
  opacity: 0;
}
</style>
