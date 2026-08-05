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
      <div class="profile-info">
        <div class="profile-meta">
          <span v-if="genderLabel" class="tag tag-default">{{ genderLabel }}</span>
          <span v-if="user?.age" class="tag tag-default">{{ user.age }} 岁</span>
          <span v-if="user?.height_cm" class="tag tag-default">身高 {{ user.height_cm }} cm</span>
          <span v-if="user?.weight_kg" class="tag tag-default">体重 {{ user.weight_kg }} kg</span>
          <span v-if="!user?.age && !user?.gender" class="text-xs text-muted">未填写档案（按成人通用标准推荐）</span>
        </div>
        <button class="btn btn-outline btn-sm" @click="openEdit">&#x270F;&#xFE0F; 编辑档案</button>
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

        <!-- 对照《膳食指南》雷达图 + AI 解读 -->
        <div v-if="assessment && assessment.days > 0 && assessment.actual.calories > 0" class="radar-section">
          <h4 class="radar-title">📊 对照《膳食指南(2022)》推荐量</h4>
          <canvas ref="radarCanvas" class="radar-canvas"></canvas>
          <div class="assessment-status">
            <span v-for="(s, k) in assessment.status" :key="k" class="tag" :class="statusClass(s)">{{ statusLabel(k, s) }}</span>
          </div>
          <button class="btn btn-primary btn-sm" style="margin-top: 8px" @click="interpret" :disabled="aiLoading">
            {{ aiLoading ? 'AI 解读中...' : '🤖 AI 健康解读' }}
          </button>
          <div v-if="aiInterp" class="ai-interp">{{ aiInterp }}</div>
        </div>
      </div>
    </div>

    <!-- 退出 -->
    <div style="margin-top: var(--spacing-xl);">
      <button class="btn btn-outline" style="color: var(--color-danger); border-color: var(--color-danger);" @click="handleLogout">
        退出登录
      </button>
    </div>

    <!-- 编辑档案弹窗 -->
    <div v-if="showEdit" class="modal-overlay" @click.self="showEdit = false">
      <div class="modal-content card">
        <h3>编辑个人信息</h3>
        <p class="text-xs text-muted" style="margin-bottom: 12px">昵称必填；个人档案（用于个性化营养建议）可留空</p>
        <div class="form-group">
          <label class="form-label">昵称</label>
          <input v-model="editForm.nickname" type="text" class="input" placeholder="给自己起个名字" />
        </div>
        <div class="form-group">
          <label class="form-label">性别</label>
          <select v-model="editForm.gender" class="input">
            <option value="">未填写</option>
            <option value="male">男</option>
            <option value="female">女</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">年龄</label>
          <input v-model="editForm.age" type="number" class="input" min="1" max="120" placeholder="留空则按成人通用" />
        </div>
        <div class="form-group">
          <label class="form-label">身高（cm）</label>
          <input v-model="editForm.height_cm" type="number" class="input" min="50" max="250" placeholder="留空则按成人通用" />
        </div>
        <div class="form-group">
          <label class="form-label">体重（kg）</label>
          <input v-model="editForm.weight_kg" type="number" class="input" min="10" max="300" placeholder="留空则按成人通用" />
        </div>
        <div class="modal-actions">
          <button class="btn btn-outline" @click="showEdit = false">取消</button>
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
        <p v-if="saveMsg" class="text-sm" :style="{ color: saveOk ? '#52c41a' : '#e74c3c', marginTop: '8px' }">{{ saveMsg }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getPreferences, getNutrition, getNutritionAssessment } from '@/api/diet'
import { updateProfile } from '@/api/auth'

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

// 个人档案编辑
const showEdit = ref(false)
const saving = ref(false)
const saveMsg = ref('')
const saveOk = ref(false)
const editForm = reactive({ nickname: '', age: '', gender: '', height_cm: '', weight_kg: '' })

const genderLabel = computed(() => {
  if (user.value?.gender === 'male') return '男'
  if (user.value?.gender === 'female') return '女'
  return ''
})

function openEdit() {
  editForm.nickname = user.value?.nickname ?? ''
  editForm.age = user.value?.age ?? ''
  editForm.gender = user.value?.gender ?? ''
  editForm.height_cm = user.value?.height_cm ?? ''
  editForm.weight_kg = user.value?.weight_kg ?? ''
  saveMsg.value = ''
  showEdit.value = true
}

async function saveProfile() {
  // 昵称必填：留空时弹提示且不执行保存
  if (!editForm.nickname.trim()) {
    saveMsg.value = '昵称不能为空，请输入昵称'
    saveOk.value = false
    return
  }
  saving.value = true
  saveMsg.value = ''
  try {
    const payload = {
      nickname: editForm.nickname.trim(),
      age: editForm.age ? Number(editForm.age) : null,
      gender: editForm.gender || null,
      height_cm: editForm.height_cm ? Number(editForm.height_cm) : null,
      weight_kg: editForm.weight_kg ? Number(editForm.weight_kg) : null,
    }
    const res = await updateProfile(payload)
    user.value = res
    localStorage.setItem('user', JSON.stringify(res))
    window.dispatchEvent(new CustomEvent('user-updated'))  // 通知导航栏立即刷新昵称
    showEdit.value = false
    saveMsg.value = '已保存'
    saveOk.value = true
  } catch (e) {
    saveMsg.value = e.message || '保存失败'
    saveOk.value = false
  } finally {
    saving.value = false
  }
}

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
    nutritionLoaded.value = true  // 先激活 v-else 分支，让柱状图 canvas 挂载，再绘制
    await nextTick()
    drawBarChart()
  } catch {
    nutritionLoaded.value = true
  }
  loadAssessment()
}

// ===== 营养对照《膳食指南》评估（雷达图 + AI 解读）=====
const assessment = ref(null)
const radarCanvas = ref(null)
const aiInterp = ref('')
const aiLoading = ref(false)

async function loadAssessment() {
  try {
    const res = await getNutritionAssessment(selectedDays.value)
    assessment.value = res
    await nextTick()
    drawRadar()
  } catch { /* ignore */ }
}

const statusLabel = (k, s) => ({ calories: '热量', protein: '蛋白质', fat: '脂肪', carbs: '碳水' }[k] + '：' + s)
const statusClass = (s) => (s === '正常' ? 'tag-default' : s === '偏高' ? 'tag-warn' : 'tag-default')

function drawRadar() {
  const canvas = radarCanvas.value
  if (!canvas || !assessment.value) return
  // DPR 高清渲染（避免模糊）
  const dpr = window.devicePixelRatio || 1
  const cssW = 300, cssH = 260
  canvas.width = cssW * dpr
  canvas.height = cssH * dpr
  canvas.style.width = cssW + 'px'
  canvas.style.height = cssH + 'px'
  const ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  const W = cssW, H = cssH
  ctx.clearRect(0, 0, W, H)
  const cx = W / 2, cy = H / 2, R = Math.min(W, H) / 2 - 44
  const labels = ['热量', '蛋白质', '脂肪', '碳水']
  const keys = ['calories', 'protein', 'fat', 'carbs']
  const a = assessment.value
  const maxVals = keys.map(k => Math.max(a.actual[k], a.guideline[k], 1))
  // 网格
  for (let ring = 1; ring <= 4; ring++) {
    ctx.beginPath()
    for (let i = 0; i <= keys.length; i++) {
      const idx = i % keys.length
      const ang = (Math.PI * 2 / keys.length) * idx - Math.PI / 2
      const rr = R * ring / 4
      const x = cx + Math.cos(ang) * rr, y = cy + Math.sin(ang) * rr
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.strokeStyle = '#e0d5c8'; ctx.lineWidth = 1; ctx.stroke()
  }
  keys.forEach((k, i) => {
    const ang = (Math.PI * 2 / keys.length) * i - Math.PI / 2
    ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(ang) * R, cy + Math.sin(ang) * R)
    ctx.strokeStyle = '#e0d5c8'; ctx.stroke()
    ctx.fillStyle = '#3A2418'; ctx.font = '12px sans-serif'; ctx.textAlign = 'center'
    ctx.fillText(labels[i], cx + Math.cos(ang) * (R + 18), cy + Math.sin(ang) * (R + 18) + 4)
  })
  const drawPolygon = (values, color, dashed) => {
    ctx.beginPath()
    keys.forEach((k, i) => {
      const ang = (Math.PI * 2 / keys.length) * i - Math.PI / 2
      const rr = R * (values[i] / maxVals[i])
      const x = cx + Math.cos(ang) * rr, y = cy + Math.sin(ang) * rr
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    })
    ctx.closePath()
    ctx.strokeStyle = color; ctx.lineWidth = 2
    if (dashed) ctx.setLineDash([5, 4])
    ctx.stroke(); ctx.setLineDash([])
    ctx.fillStyle = dashed ? 'rgba(217,161,91,0.10)' : 'rgba(230,126,34,0.07)'
    ctx.fill()
  }
  drawPolygon(keys.map(k => a.guideline[k]), '#D9A15B', true)
  drawPolygon(keys.map(k => a.actual[k]), '#E67E22', false)
  ctx.fillStyle = '#B87D3A'; ctx.font = '11px sans-serif'; ctx.textAlign = 'left'
  ctx.fillText('— 推荐（膳食指南）', 10, 22)
  ctx.fillStyle = '#E67E22'
  ctx.fillText('— 你的日均摄入', 10, 40)
}

async function interpret() {
  aiLoading.value = true
  aiInterp.value = ''
  const token = localStorage.getItem('token')
  try {
    const resp = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
      body: JSON.stringify({ content: '请解读我的营养分析数据（对照膳食指南推荐量）。要求：先用一句话总结整体状况，再列出3-5条具体可执行的调整建议（每条带依据），简洁结构化、一目了然，总字数200字以内。', session_id: 'about-nutrition' }),
    })
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = '', currentEvent = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const lines = buf.split('\n')
      buf = lines.pop() || ''
      for (const line of lines) {
        const t = line.trim()
        if (t.startsWith('event:')) currentEvent = t.slice(6).trim()
        else if (t.startsWith('data:')) {
          try {
            const data = JSON.parse(t.slice(5).trim())
            if (currentEvent === 'token') aiInterp.value += data.content || ''
          } catch { /* 忽略 */ }
        }
      }
    }
  } catch { aiInterp.value = '解读失败，请重试' }
  finally { aiLoading.value = false }
}

function drawBarChart() {
  const canvas = barCanvas.value
  if (!canvas || !nutrition.value.days.length) return
  // DPR 高清渲染：分辨率匹配显示尺寸 × devicePixelRatio，修复高 DPI 屏模糊
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  const W = Math.round(rect.width) || canvas.width
  const H = Math.round(rect.height) || canvas.height
  canvas.width = W * dpr
  canvas.height = H * dpr
  canvas.style.width = W + 'px'
  canvas.style.height = H + 'px'
  const ctx = canvas.getContext('2d')
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
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
/* 营养对照《膳食指南》雷达图 */
.radar-section {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-md);
  border-top: 1px dashed var(--color-divider);
}
.radar-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-primary-dark);
  margin-bottom: var(--spacing-sm);
}
.radar-canvas {
  display: block;
  margin: 0 auto;
}
.assessment-status {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: center;
  margin: var(--spacing-sm) 0;
}
.tag-warn {
  background: #FFF3E0;
  color: #E67E22;
  border-color: #F5C488;
}
.ai-interp {
  margin-top: var(--spacing-sm);
  padding: 10px 12px;
  background: var(--color-bg-warm);
  border-left: 3px solid var(--color-primary);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  line-height: 1.7;
  white-space: pre-wrap;
  text-align: left;
}

/* 编辑档案弹窗：居中遮罩 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  width: 400px;
  max-width: 90vw;
  padding: var(--spacing-lg);
}
.modal-content h3 {
  margin-bottom: 4px;
  font-size: var(--font-size-lg);
}
.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}
.profile-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: var(--spacing-sm);
}
.profile-meta {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}
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
