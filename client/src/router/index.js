import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页 — 食光记' },
  },
  {
    path: '/today-eat',
    name: 'TodayEat',
    component: () => import('../views/TodayEat.vue'),
    meta: { title: '今天吃什么' },
  },
  {
    path: '/diy',
    name: 'DIY',
    component: () => import('../views/DIY.vue'),
    meta: { title: '我的厨房' },
  },
  {
    path: '/square',
    name: 'Square',
    component: () => import('../views/Square.vue'),
    meta: { title: '美食广场' },
  },
  {
    path: '/square/:id',
    name: 'SquareDetail',
    component: () => import('../views/SquareDetail.vue'),
    meta: { title: '食谱详情' },
  },
  {
    path: '/expense',
    name: 'Expense',
    component: () => import('../views/Expense.vue'),
    meta: { title: '记账' },
  },
  {
    path: '/assistant',
    name: 'Assistant',
    component: () => import('../views/Assistant.vue'),
    meta: { title: 'AI 助手' },
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: { title: '关于我' },
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册' },
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('../views/AdminLogin.vue'),
    meta: { title: '管理员登录' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/Admin.vue'),
    meta: { title: '管理后台', requireAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// 检查当前 token 的用户是否是管理员
function isAdminUser() {
  try {
    const userStr = localStorage.getItem('user')
    if (!userStr) return false
    const user = JSON.parse(userStr)
    return !!user.is_admin
  } catch {
    return false
  }
}

// 路由守卫：未登录 → 登录页；非管理员 → 管理员登录页
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const publicPages = ['Login', 'Register', 'AdminLogin']

  // 需要管理员权限的路由
  if (to.meta.requireAdmin) {
    if (!token) {
      return next('/admin/login')
    }
    if (!isAdminUser()) {
      // 已登录但不是管理员 → 跳转到管理员登录页
      return next('/admin/login')
    }
    return next()
  }

  if (!token && !publicPages.includes(to.name)) {
    next('/login')
  } else {
    next()
  }
})

// 设置页面标题
router.afterEach((to) => {
  document.title = to.meta.title || '食光记'
})

export default router
