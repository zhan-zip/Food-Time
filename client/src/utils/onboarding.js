/**
 * 新用户引导（driver.js）
 * 注册成功后 localStorage 写入 onboard_pending，首页挂载时触发一次引导，
 * 完成或跳过后清除标记，不再重复弹出。
 */
import { driver } from 'driver.js'
import 'driver.js/dist/driver.css'

const STEPS = [
  {
    element: '.navbar-logo',
    popover: {
      title: '👋 欢迎来到食光记',
      description: '我是你的 AI 智能饮食助手，帮你解决「今天吃什么」的每一刻。先用 30 秒带你认识各个功能～',
      side: 'bottom',
      align: 'start',
    },
  },
  {
    element: '[data-nav="/today-eat"]',
    popover: {
      title: '🍲 今天吃什么',
      description: '搜索食物、记录每天吃了什么；还能拍照识别食材，直接获得菜谱建议。',
      side: 'bottom',
    },
  },
  {
    element: '[data-nav="/diy"]',
    popover: {
      title: '🔪 我的厨房',
      description: '打开冰箱选食材，AI 帮你出烹饪建议，还能保存成自己的菜谱。',
      side: 'bottom',
    },
  },
  {
    element: '[data-nav="/square"]',
    popover: {
      title: '🌍 美食广场',
      description: '看看别人分享的食谱，喜欢就收藏进自己的食谱库。',
      side: 'bottom',
    },
  },
  {
    element: '[data-nav="/expense"]',
    popover: {
      title: '💰 记账',
      description: '记录饮食消费，拍小票 AI 自动识别金额和分类。',
      side: 'bottom',
    },
  },
  {
    element: '[data-nav="/assistant"]',
    popover: {
      title: '🤖 AI 助手',
      description: '随时和 AI 聊天，帮你选菜、分析营养、管理健康。',
      side: 'bottom',
    },
  },
  {
    element: '[data-nav="/about"]',
    popover: {
      title: '👤 关于我',
      description: '查看个人档案、饮食偏好和营养分析报告。',
      side: 'bottom',
    },
  },
]

export function maybeStartOnboarding() {
  if (!localStorage.getItem('onboard_pending')) return
  const driverObj = driver({
    showProgress: true,
    animate: true,
    allowClose: true,
    overlayColor: 'rgba(0,0,0,0.55)',
    steps: STEPS,
    onDestroyed: () => {
      localStorage.removeItem('onboard_pending')
    },
  })
  driverObj.drive()
}
