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
      <div v-if="!prefLoaded" class="text-muted text-sm">加载中...</div>
      <div v-else>
        <div class="pref-grid">
          <div class="pref-item">
            <span class="pref-label">辣度</span>
            <div class="pref-bar"><div class="pref-fill" :style="{ width: (pref.spicy_level * 100) + '%', background: '#e74c3c' }"></div></div>
            <span class="pref-val">{{ Math.round(pref.spicy_level * 100) }}%</span>
          </div>
          <div class="pref-item">
            <span class="pref-label">甜度</span>
            <div class="pref-bar"><div class="pref-fill" :style="{ width: (pref.sweet_level * 100) + '%', background: '#f39c12' }"></div></div>
            <span class="pref-val">{{ Math.round(pref.sweet_level * 100) }}%</span>
          </div>
          <div class="pref-item">
            <span class="pref-label">热食偏好</span>
            <div class="pref-bar"><div class="pref-fill" :style="{ width: (pref.hot_cold_ratio * 100) + '%', background: '#e67e22' }"></div></div>
            <span class="pref-val">{{ Math.round(pref.hot_cold_ratio * 100) }}%</span>
          </div>
        </div>
        <div style="margin-top: 12px">
          <span class="text-sm text-secondary">偏好菜系：</span>
          <span v-if="pref.fav_cuisines?.length" class="text-sm">
            <span v-for="c in uniqueCuisines" :key="c" class="tag tag-default" style="margin: 2px">{{ c }}</span>
          </span>
          <span v-else class="text-muted text-sm">暂无数据，多记录饮食即可自动生成</span>
        </div>
        <p class="text-xs text-muted" style="margin-top: 8px">共记录 {{ pref.total_records }} 次饮食</p>
      </div>
    </div>

    <!-- 营养分析 -->
    <div class="card" style="margin-top: var(--spacing-md);">
      <h3 class="card-title">&#x1F4C8; 营养分析</h3>
      <div style="margin-bottom: 12px">
        <button
          v-for="d in [7, 30]"
          :key="d"
          class="tag"
          :class="selectedDays === d ? 'tag-primary' : 'tag-default'"
          style="cursor: pointer"
          @click="loadNutrition(d)"
        >
          最近 {{ d }} 天
        </button>
      </div>
      <div v-if="!nutritionLoaded" class="text-muted text-sm">加载中...</div>
      <div v-else-if="nutrition.total_days === 0" class="text-muted text-sm">
        暂无饮食记录，去<a href="/today-eat" style="color: var(--color-primary)">今天吃什么</a>记录你的第一餐吧！
      </div>
      <div v-else>
        <!-- 柱状图 -->
        <canvas ref="barCanvas" width="600" height="260" class="chart-canvas"></canvas>
        <!-- 摘要 -->
        <div class="nutrition-summary">
          <div class="summary-item">
            <span class="summary-val">{{ nutrition.avg_calories }}</span>
            <span class="summary-label">日均热量<br/>kcal</span>
          </div>
          <div class="summary-item">
            <span class="summary-val">{{ nutrition.avg_protein }}</span>
            <span class="summary-label">日均蛋白质<br/>g</span>
          </div>
          <div class="summary-item">
            <span class="summary-val">{{ nutrition.avg_fat }}</span>
            <span class="summary-label">日均脂肪<br/>g</span>
          </div>
          <div class="summary-item">
            <span class="summary-val">{{ nutrition.avg_carbs }}</span>
            <span class="summary-label">日均碳水<br/>g</span>
          </div>
        </div>
      </div>
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
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getPreferences, getNutrition } from '@/api/diet'

const router = useRouter()
const user = ref(null)

// 偏好
const prefLoaded = ref(false)
const pref = ref({ spicy_level: 0, sweet_level: 0, hot_cold_ratio: 0.5, fav_cuisines: [], fav_tags: [], total_records: 0 })

const uniqueCuisines = computed(() => {
  return [...new Set(pref.value.fav_cuisines || [])]
})

// 营养
const selectedDays = ref(7)
const nutritionLoaded = ref(false)
const nutrition = ref({ days: [], avg_calories: 0, avg_protein: 0, avg_fat: 0, avg_carbs: 0, total_days: 0 })
const barCanvas = ref(null)

onMounted(() => {
  try {
    user.value = JSON.parse(localStorage.getItem('user'))
  } catch { /* ignore */ }
  loadPrefs()
  loadNutrition(7)
})

async function loadPrefs() {
  try {
    const res = await getPreferences()
    pref.value = res
  } catch { /* ignore */ }
  prefLoaded.value = true
}

async function loadNutrition(days) {
  selectedDays.value = days
  nutritionLoaded.value = false
  try {
    const res = await getNutrition(days)
    nutrition.value = res
    await nextTick()
    drawBarChart()
  } catch { /* ignore */ }
  nutritionLoaded.value = true
}

function drawBarChart() {
  const canvas = barCanvas.value
  if (!canvas || !nutrition.value.days.length) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width
  const H = canvas.height
  const pad = { top: 30, right: 20, bottom: 50, left: 60 }
  const pw = W - pad.left - pad.right
  const ph = H - pad.top - pad.bottom

  ctx.clearRect(0, 0, W, H)

  const days = nutrition.value.days.slice(-14) // 最多显示 14 天
  if (!days.length) return

  // 找最大值
  let maxVal = 0
  days.forEach(d => {
    [d.calories, d.protein, d.fat, d.carbs].forEach(v => {
      if (v > maxVal) maxVal = v
    })
  })
  maxVal = Math.ceil(maxVal / 100) * 100 || 100

  // 网格线
  ctx.strokeStyle = '#eee'
  ctx.lineWidth = 1
  ctx.font = '10px sans-serif'
  ctx.fillStyle = '#999'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + ph * (1 - i / 4)
    ctx.beginPath()
    ctx.moveTo(pad.left, y)
    ctx.lineTo(W - pad.right, y)
    ctx.stroke()
    ctx.textAlign = 'right'
    ctx.fillText(Math.round(maxVal * i / 4), pad.left - 8, y + 4)
  }

  const bw = Math.min(36, pw / days.length - 8)
  const gap = Math.max(2, (pw - bw * days.length) / (days.length + 1))

  const barColors = [
    { key: 'calories', color: '#D9A15B', label: '热量' },
    { key: 'protein', color: '#52c41a', label: '蛋白' },
    { key: 'fat', color: '#f39c12', label: '脂肪' },
    { key: 'carbs', color: '#3498db', label: '碳水' },
  ]

  // 绘制分组柱状图
  const groupW = bw * barColors.length + gap * (barColors.length - 1)
  const groupGap = Math.max(2, (pw - groupW * days.length) / (days.length + 1))

  days.forEach((d, di) => {
    const gx = pad.left + groupGap * (di + 1) + groupW * di
    barColors.forEach((bc, bi) => {
      const val = (d[bc.key] || 0)
      const barH = (val / maxVal) * ph
      const bx = gx + bi * (bw + gap)
      const by = pad.top + ph - barH

      ctx.fillStyle = bc.color
      ctx.fillRect(bx, by, bw, barH)
    })

    // 日期标签
    const dateStr = d.date.slice(5) // MM-DD
    ctx.fillStyle = '#999'
    ctx.textAlign = 'center'
    ctx.font = '10px sans-serif'
    ctx.fillText(dateStr, gx + groupW / 2, H - pad.bottom + 30)
  })

  // 图例
  const legendY = H - 8
  let lx = pad.left
  ctx.font = '10px sans-serif'
  barColors.forEach(bc => {
    ctx.fillStyle = bc.color
    ctx.fillRect(lx, legendY - 8, 10, 10)
    ctx.fillStyle = '#666'
    ctx.textAlign = 'left'
    ctx.fillText(bc.label, lx + 14, legendY)
    lx += 60
  })
}

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

/* 偏好条 */
.pref-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.pref-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.pref-label {
  width: 70px;
  font-size: 13px;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}
.pref-bar {
  flex: 1;
  height: 12px;
  background: var(--color-bg-warm);
  border-radius: 6px;
  overflow: hidden;
}
.pref-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}
.pref-val {
  width: 36px;
  font-size: 12px;
  color: var(--color-text-muted);
  text-align: right;
}

/* 图表 */
.chart-canvas {
  width: 100%;
  max-width: 600px;
  height: auto;
  display: block;
  margin: 0 auto;
}

/* 摘要 */
.nutrition-summary {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-top: var(--spacing-md);
  flex-wrap: wrap;
}
.summary-item {
  text-align: center;
  padding: 10px 16px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  min-width: 80px;
}
.summary-val {
  display: block;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
}
.summary-label {
  font-size: 11px;
  color: var(--color-text-muted);
  line-height: 1.4;
}
</style>
