<template>
  <div id="site-container">
    <!-- 登录/注册等无导航页 -->
    <template v-if="isMinimalPage">
      <router-view />
    </template>

    <!-- 正常页面：顶部导航 + 内容 -->
    <template v-else>
      <!-- 顶部导航栏 -->
      <header class="navbar" :class="{ 'navbar--collapsed': sidebarOpen }">
        <div class="navbar-inner container">
          <!-- Logo -->
          <router-link to="/" class="navbar-logo" @click="closeSidebar">
            <span class="logo-icon">&#x1F372;</span>
            <span class="logo-text">食光记</span>
          </router-link>

          <!-- 桌面端导航链接 -->
          <nav class="navbar-links" ref="navLinks">
            <router-link
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              :data-nav="item.to"
              class="navbar-link"
              active-class="navbar-link--active"
              @click="closeSidebar"
            >
              <span class="navbar-link-icon">{{ item.icon }}</span>
              <span>{{ item.label }}</span>
            </router-link>
          </nav>

          <!-- 右侧操作区 -->
          <div class="navbar-actions">
            <!-- 登录/用户状态 -->
            <template v-if="isLoggedIn">
              <router-link to="/about" class="navbar-link" active-class="navbar-link--active" data-nav="/about">
                <span class="navbar-link-icon">&#x1F464;</span>
                <span class="navbar-link-label">{{ userNickname }}</span>
              </router-link>
            </template>
            <template v-else>
              <router-link to="/login" class="btn btn-outline btn-sm">登录</router-link>
            </template>

            <!-- 切换侧边栏按钮 -->
            <button class="navbar-toggle" @click="toggleSidebar" :title="sidebarOpen ? '收起菜单' : '展开菜单'">
              <span v-if="!sidebarOpen">&#x2630;</span>
              <span v-else>&#x2715;</span>
            </button>
          </div>
        </div>
      </header>

      <!-- 左侧竖向导航栏（切换后显示） -->
      <aside class="sidebar" :class="{ 'sidebar--open': sidebarOpen }" @click.self="closeSidebar">
        <nav class="sidebar-nav">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            :data-nav="item.to"
            class="sidebar-link"
            active-class="sidebar-link--active"
            @click="closeSidebar"
          >
            <span class="sidebar-link-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </router-link>
          <div class="sidebar-divider"></div>
          <template v-if="isLoggedIn">
            <router-link to="/about" class="sidebar-link" active-class="sidebar-link--active" data-nav="/about" @click="closeSidebar">
              <span class="sidebar-link-icon">&#x1F464;</span>
              <span>{{ userNickname }}</span>
            </router-link>
          </template>
          <template v-else>
            <router-link to="/login" class="sidebar-link" @click="closeSidebar">
              <span class="sidebar-link-icon">&#x1F511;</span>
              <span>登录</span>
            </router-link>
          </template>
        </nav>
      </aside>

      <!-- 遮罩层 -->
      <div class="sidebar-overlay" v-if="sidebarOpen" @click="closeSidebar"></div>

      <!-- 主内容区 -->
      <main class="main-content">
        <router-view />
      </main>

      <!-- 页脚 -->
      <footer class="site-footer">
        <div class="container">
          <p>&copy; 2026 食光记 &mdash; AI 驱动的智能饮食助手</p>
        </div>
      </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const sidebarOpen = ref(false)
const userNickname = ref('')
const token = ref(localStorage.getItem('token'))

// 无导航页（登录/注册/管理后台）
const noNavPages = ['Login', 'Register', 'Admin']
const isMinimalPage = computed(() => noNavPages.includes(route.name))

// 是否已登录
const isLoggedIn = computed(() => !!token.value)

// 导航项
const navItems = [
  { to: '/',          label: '首页',       icon: '\u{1F3E0}' },  // 🏠
  { to: '/today-eat', label: '今天吃什么', icon: '\u{1F372}' },  // 🍲
  { to: '/diy',       label: '我的厨房',   icon: '\u{1F52A}' },  // 🔪
  { to: '/square',    label: '美食广场',   icon: '\u{1F30D}' },  // 🌍
  { to: '/expense',   label: '记账',       icon: '\u{1F4B0}' },  // 💰
  { to: '/assistant', label: 'Agent 助手', icon: '\u{1F916}' },  // 🤖
]

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function closeSidebar() {
  sidebarOpen.value = false
}

// 加载用户信息
async function loadUserInfo() {
  if (!token.value) return
  try {
    const res = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    if (res.ok) {
      const data = await res.json()
      userNickname.value = data.nickname || data.email
    } else {
      // 修复 M9：token 无效/过期 → 清除登录状态，避免"已登录但无昵称"
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  } catch {
    // 网络错误（服务器不可达）不强制登出，避免网络抖动导致掉线
  }
}

// 监听「用户信息已更新」事件（About 页保存档案后派发），立即刷新导航栏昵称
function onUserUpdated() {
  loadUserInfo()
}

onMounted(() => {
  loadUserInfo()
  window.addEventListener('user-updated', onUserUpdated)
})

onBeforeUnmount(() => {
  window.removeEventListener('user-updated', onUserUpdated)
})

// 监听路由变化刷新 token 状态
watch(() => route.path, () => {
  token.value = localStorage.getItem('token')
  if (token.value) loadUserInfo()
  closeSidebar()
})
</script>

<style scoped>
/* ============================================================
   顶部导航栏
   ============================================================ */
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--navbar-height);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-divider);
  transition: all 0.3s ease;
}

.navbar-inner {
  display: flex;
  align-items: center;
  height: 100%;
  gap: var(--spacing-md);
}

/* Logo */
.navbar-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text);
  flex-shrink: 0;
  margin-right: var(--spacing-md);
}
.logo-icon {
  font-size: 24px;
}
.logo-text {
  letter-spacing: 1px;
}

/* 桌面端导航链接 */
.navbar-links {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.navbar-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  transition: all 0.2s;
  white-space: nowrap;
}
.navbar-link:hover {
  background: var(--color-bg-warm);
  color: var(--color-text);
}
.navbar-link--active {
  background: rgba(217, 161, 91, 0.12);
  color: var(--color-primary-dark);
  font-weight: 600;
}
.navbar-link-icon {
  font-size: 16px;
}

/* 右侧操作区 */
.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

/* 切换按钮 */
.navbar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--color-text);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
}
.navbar-toggle:hover {
  background: var(--color-bg-warm);
}

/* ============================================================
   左侧竖向导航栏
   ============================================================ */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 200;
  width: 260px;
  height: 100vh;
  background: var(--color-bg-card);
  box-shadow: var(--shadow-xl);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow-y: auto;
  padding-top: var(--navbar-height);
}
.sidebar--open {
  transform: translateX(0);
}

.sidebar-nav {
  padding: var(--spacing-md);
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  transition: all 0.2s;
  margin-bottom: 2px;
}
.sidebar-link:hover {
  background: var(--color-bg-warm);
}
.sidebar-link--active {
  background: rgba(217, 161, 91, 0.12);
  color: var(--color-primary-dark);
  font-weight: 600;
}
.sidebar-link-icon {
  font-size: 20px;
  width: 24px;
  text-align: center;
}

.sidebar-divider {
  height: 1px;
  background: var(--color-divider);
  margin: var(--spacing-sm) 0;
}

/* 遮罩 */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  z-index: 150;
  background: rgba(0, 0, 0, 0.3);
  display: none;
}

/* ============================================================
   主内容
   ============================================================ */
.main-content {
  min-height: calc(100vh - var(--navbar-height) - 60px);
}

.site-footer {
  text-align: center;
  padding: var(--spacing-lg);
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  border-top: 1px solid var(--color-divider);
}

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 768px) {
  .navbar-links {
    display: none;           /* 小屏隐藏桌面导航链接 */
  }
  .navbar-link-label {
    display: none;           /* 只显示图标 */
  }
  .navbar-toggle {
    display: block;          /* 显示汉堡菜单按钮 */
  }
  .sidebar-overlay {
    display: block;          /* 小屏显示遮罩 */
  }
}
</style>
