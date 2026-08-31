import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './assets/main.css'
import { registerSW } from 'virtual:pwa-register'
// 注册 Service Worker（PWA 可安装 + 离线缓存）；immediate: true 表示页面加载后立即注册
registerSW({ immediate: true })

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#site-root')
