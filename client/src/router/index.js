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

// 路由守卫：未登录跳转登录页
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  const publicPages = ['Login', 'Register']

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
