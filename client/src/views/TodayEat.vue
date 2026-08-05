<template>
  <div class="page container page-section">
    <h2 class="section-title">今天吃什么</h2>

    <!-- Tab 切换 -->
    <div class="tab-bar">
      <button class="tab-btn" :class="{ active: tab === 'search' }" @click="tab = 'search'">
        &#x1F50D; 搜索浏览
      </button>
      <button class="tab-btn" :class="{ active: tab === 'decide' }" @click="tab = 'decide'">
        &#x1F3AF; 辅助决策
      </button>
    </div>

    <!-- ====== Tab 1: 搜索浏览 ====== -->
    <div v-show="tab === 'search'">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <input
          v-model="keyword"
          class="input"
          placeholder="搜索食物名称..."
          @keyup.enter="search"
        />
        <button class="btn btn-primary" @click="search">搜索</button>
      </div>

      <!-- 快捷筛选（独立明显按钮） -->
      <div class="custom-filter-bar">
        <button
          class="btn custom-btn"
          :class="viewMode === 'diy' ? 'btn-primary' : 'btn-outline'"
          @click="toggleCustom"
        >
          🍳 只看我的 DIY 菜谱
        </button>
        <button
          class="btn custom-btn"
          :class="viewMode === 'fav' ? 'btn-primary' : 'btn-outline'"
          @click="toggleFav"
        >
          ⭐ 我收藏的食谱
        </button>
      </div>

      <!-- 分类筛选 -->
      <div class="filter-tags">
        <button
          v-for="cat in normalCategories"
          :key="cat.id"
          class="tag"
          :class="selectedCat === cat.id ? 'tag-primary' : 'tag-default'"
          style="cursor: pointer"
          @click="selectCategory(cat.id)"
        >
          {{ cat.name }}
        </button>
        <button class="tag tag-default" style="cursor: pointer" @click="selectCategory(null)">全部</button>
      </div>

      <!-- 结果列表 -->
      <div v-if="loading" class="text-center text-muted" style="padding: 40px 0">搜索中...</div>
      <div v-else-if="foods.length === 0" class="text-center text-muted" style="padding: 40px 0">
        暂无结果，试试其他关键词
      </div>
      <div v-else class="food-grid">
        <div class="card food-card" v-for="food in foods" :key="food.id" :class="{ 'can-click': food.has_recipe }" @click="food.has_recipe && goDetail(food)">
          <div class="food-card-img"><FoodImage :name="food.name" :use-pixabay="false" /></div>
          <div class="food-card-body">
            <h3>{{ food.name }}</h3>
            <p class="text-sm text-secondary">{{ food.cuisine || '通用' }}</p>
            <div class="food-card-meta">
              <span class="tag tag-default">{{ food.category_name }}</span>
              <span class="text-xs text-muted">{{ food.calories_per_100g || 0 }} kcal/100g</span>
            </div>
            <button class="btn btn-primary btn-sm" style="width:100%; margin-top:10px" @click.stop="openRecordModal(food)">
              我吃了这个
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ====== Tab 2: 辅助决策 ====== -->
    <div v-show="tab === 'decide'" class="decide-stack">
      <!-- ① 食材识别（拍照/上传 → Qwen 识别 → 库匹配 → AI 建议） -->
      <div class="card decide-card">
        <h3 class="decide-card-title">&#x1F4F7; 食材识别</h3>

        <input ref="ingInput" type="file" accept="image/*" capture="environment" style="display:none" @change="onIngredientUpload" />

        <div v-if="ingLoading" class="text-center text-muted text-sm" style="padding:24px 0">🤖 正在识别食材...</div>
        <div v-else-if="!recognizedIngredients.length" class="text-center text-muted text-sm" style="padding:24px 0; cursor:pointer" @click="triggerIngUpload">
          📷 拍照或上传食材照片<br/><span style="font-size:12px">AI 自动识别有什么食材</span>
        </div>

        <template v-else>
          <p class="text-sm text-secondary" style="margin-bottom:8px">识别到以下食材（点击可移除）：</p>
          <div class="ing-chip-list">
            <span v-for="(ing, i) in recognizedIngredients" :key="'ing' + i" class="tag tag-primary ing-chip" @click="removeIngredient(i)">{{ ing }} ✕</span>
          </div>
          <p v-if="recognizedSeasonings.length" class="text-sm text-secondary" style="margin:8px 0 4px">调料：</p>
          <div class="ing-chip-list">
            <span v-for="(s, i) in recognizedSeasonings" :key="'sea' + i" class="tag tag-default ing-chip" @click="removeSeasoning(i)">{{ s }} ✕</span>
          </div>
          <button class="btn btn-primary btn-sm" style="width:100%; margin-top:10px" :disabled="suggestLoading" @click="getSuggestionFromImage">
            {{ suggestLoading ? 'AI 匹配中...' : '🔍 获取烹饪建议' }}
          </button>
          <button class="btn btn-outline btn-sm" style="width:100%; margin-top:6px" @click="resetIngredient">🔄 重新拍照</button>
        </template>

        <div v-if="ingSuggestion" class="ing-suggestion" style="margin-top:12px">
          <div v-if="ingSuggestion.matched && ingSuggestion.matched.length">
            <p class="text-sm text-secondary" style="margin-bottom:6px">🍽️ 库中已找到相似菜谱：</p>
            <div v-for="m in ingSuggestion.matched" :key="m.id" class="matched-recipe">
              <strong>{{ m.name }}</strong>
              <span v-if="m.cuisine" class="tag tag-default tag-sm" style="margin-left:6px">{{ m.cuisine }}</span>
              <span v-if="m.calories_per_100g" class="text-muted text-xs" style="margin-left:6px">{{ m.calories_per_100g }} kcal/100g</span>
            </div>
          </div>
          <div v-if="ingSuggestion.ai_suggestion" class="ai-suggestion-box">
            <p class="text-sm" style="font-weight:600; margin-bottom:6px">{{ ingSuggestion.ai_suggestion.name }}</p>
            <p class="text-xs text-muted" style="margin-bottom:6px">{{ ingSuggestion.ai_suggestion.cooking_method_label }} · {{ ingSuggestion.ai_suggestion.estimated_time }} · 约 {{ ingSuggestion.ai_suggestion.estimated_calories }} kcal/100g</p>
            <ol class="text-sm" style="padding-left:18px; line-height:1.7">
              <li v-for="(step, si) in ingSuggestion.ai_suggestion.steps" :key="si">{{ step }}</li>
            </ol>
            <p v-if="ingSuggestion.ai_suggestion.nutrition_tip" class="text-xs text-muted" style="margin-top:6px">💡 {{ ingSuggestion.ai_suggestion.nutrition_tip }}</p>
          </div>
          <p v-if="ingSuggestion.error" class="text-sm" style="color:var(--color-danger); margin-top:8px">{{ ingSuggestion.error }}</p>
        </div>
      </div>

      <!-- ② 筛选条件 FR-21 -->
      <div class="card decide-card">
          <h3 class="decide-card-title">&#x1F4CB; 筛选条件</h3>

          <div class="form-group">
            <label class="form-label">辣度</label>
            <div class="meal-btns">
              <button
                v-for="s in spicyOptions" :key="s.value"
                class="tag tag-sm"
                :class="filterForm.spicy === s.value ? 'tag-primary' : 'tag-default'"
                style="cursor: pointer"
                @click="filterForm.spicy = filterForm.spicy === s.value ? '' : s.value"
              >{{ s.label }}</button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">菜系</label>
            <select v-model="filterForm.cuisine" class="input input-sm">
              <option value="">不限</option>
              <option v-for="c in allCuisineOptions" :key="c" :value="c">{{ c }}</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">热量上限 (kcal/100g)</label>
            <div class="range-row">
              <input v-model.number="filterForm.maxCal" class="input input-sm" type="number" min="0" max="1000" placeholder="不限" style="width:100px" />
              <span class="text-xs text-muted">{{ filterForm.maxCal ? '≤ ' + filterForm.maxCal + ' kcal' : '不设上限' }}</span>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">烹饪方式</label>
            <select v-model="filterForm.cookMethod" class="input input-sm">
              <option value="">不限</option>
              <option value="炒">炒</option>
              <option value="蒸">蒸</option>
              <option value="煮">煮</option>
              <option value="烤">烤</option>
              <option value="炸">炸</option>
              <option value="炖">炖</option>
              <option value="凉拌">凉拌</option>
            </select>
          </div>

          <button class="btn btn-primary" style="width:100%; margin-top:8px" @click="applyFilterFromDecide">
            &#x1F50D; 应用筛选到结果列表
          </button>
        </div>

        <!-- 附近美食 FR-24 -->
        <div class="card decide-card">
          <h3 class="decide-card-title">&#x1F4CD; 附近美食</h3>
          <p v-if="nearbyCity" class="text-sm text-secondary" style="margin-bottom:12px">
            你的城市：<strong>{{ nearbyCity }}</strong>
            <span
              class="city-edit-link"
              style="cursor:pointer; margin-left:6px; color:var(--color-primary);"
              @click="manualCityMode = !manualCityMode"
            >或许你想换个定位</span>
          </p>
          <p v-else class="text-sm text-muted" style="margin-bottom:12px">
            正在定位...
          </p>
          <div v-if="manualCityMode" style="display:flex; gap:8px; margin-bottom:10px">
            <input v-model="nearbyCityInput" class="input input-sm" placeholder="输入城市名，如：枣庄" @keyup.enter="setManualCity" style="flex:1" />
            <button class="btn btn-primary btn-sm" @click="setManualCity">确定</button>
          </div>
          <button class="btn btn-outline btn-sm" style="width:100%" :disabled="nearbyLoading" @click="getNearbyRecommend">
            {{ nearbyLoading ? '查询中...' : '查看当地特色菜推荐' }}
          </button>
          <div v-if="nearbyResult" class="nearby-result-card" style="margin-top:10px">
            <div class="nearby-result-text">{{ nearbyResult }}</div>
          </div>
        </div>

        <!-- ③ 随机转盘 FR-22 -->
        <div class="card decide-card" style="text-align:center">
          <h3 class="decide-card-title">&#x1F3B0; 随机转盘</h3>

          <!-- 自定义添加食物 -->
          <div class="wheel-add-row">
            <input
              v-model="customFoodInput"
              class="input input-sm"
              placeholder="输入菜名添加..."
              @keyup.enter="addCustomFood"
              style="flex:1"
            />
            <button class="btn btn-outline btn-sm" @click="addCustomFood" :disabled="!customFoodInput.trim()">
              添加
            </button>
          </div>

          <!-- 当前转盘选项标签 -->
          <div v-if="wheelItems.length" class="wheel-tags">
            <span
              v-for="(item, idx) in wheelItems"
              :key="idx"
              class="tag tag-sm"
              :class="idx < wheelItems.length - customCount ? 'tag-default' : 'tag-warm'"
              :style="{ cursor: 'pointer', borderLeft: '3px solid ' + (item.color || '#ccc') }"
              @click="removeWheelItem(idx)"
              :title="'点击移除: ' + item.label"
            >
              {{ item.label }}
            </span>
          </div>

          <!-- 转盘 -->
          <SpinWheel v-if="wheelItems.length >= 2" :items="wheelItems" @done="onWheelDone" />
          <div v-else class="text-muted text-sm" style="padding:30px 0">
            至少需要 2 个选项才能转动转盘。<br />
            从搜索结果中加载，或手动添加。
          </div>

          <!-- 转盘结果操作 -->
          <div v-if="wheelResult" class="modal-actions" style="justify-content: center; margin-top: 12px">
            <button class="btn btn-primary btn-sm" @click="searchWheelResult">
              &#x1F50D; 查看详情
            </button>
            <button class="btn btn-outline btn-sm" @click="wheelResult = null;">
              再转一次
            </button>
          </div>

          <!-- 加载选项按钮 -->
          <div class="wheel-actions" style="margin-top:12px">
            <button class="btn btn-outline btn-sm" @click="loadFoodsToWheel" :disabled="!foods.length">
              &#x1F4E5; 加载搜索结果 ({{ foods.length }}个)
            </button>
            <button class="btn btn-outline btn-sm" @click="clearWheel" :disabled="!wheelItems.length">
              &#x1F5D1; 清空
            </button>
          </div>
      </div>
    </div>

    <!-- ====== 弹窗：饮食记录 ====== -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content card">
        <h3>记录饮食：{{ selectedFood?.name }}</h3>
        <p class="text-sm text-secondary">每100g 约 {{ selectedFood?.calories_per_100g || 0 }} kcal</p>

        <div class="form-group">
          <label class="form-label">餐别</label>
          <div class="meal-btns">
            <button
              v-for="m in mealOptions" :key="m.value"
              class="tag" :class="recordForm.meal_type === m.value ? 'tag-primary' : 'tag-default'"
              style="cursor: pointer" @click="recordForm.meal_type = m.value"
            >{{ m.label }}</button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">分量（克）</label>
          <input v-model.number="recordForm.quantity_g" class="input" type="number" min="10" max="5000" placeholder="例如 200" />
          <p class="text-xs text-muted" style="margin-top:4px">预估热量：{{ estimatedCal }} kcal</p>
          <p class="text-xs text-muted" style="margin-top:2px; color:#999">* 营养数据基于《中国食物成分表（第六版）》食材加权估算</p>
        </div>

        <div class="modal-actions">
          <button class="btn btn-outline" @click="showModal = false">取消</button>
          <button class="btn btn-primary" :disabled="!canRecord || recording" @click="submitRecord">
            {{ recording ? '记录中...' : '确认记录' }}
          </button>
        </div>
        <p v-if="recordMsg" class="text-sm" :style="{ color: recordOk ? '#52c41a' : '#e74c3c', marginTop: '8px' }">
          {{ recordMsg }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'
import { createDietRecord } from '@/api/diet'
import { getFavoriteRecipes } from '@/api/public'
import { suggestRecipe, recognizeIngredients } from '@/api/diy'
import SpinWheel from '@/components/today/SpinWheel.vue'
import FoodImage from '@/components/FoodImage.vue'
import { useRouter } from 'vue-router'

// ====== Tab ======
const tab = ref('search')

// ====== 搜索状态 ======
const keyword = ref('')
const selectedCat = ref(null)
const viewMode = ref('all')  // 'all' | 'diy' | 'fav'
const foods = ref([])
const categories = ref([])
const allCuisineOptions = ref([])
const loading = ref(false)

// ====== 筛选 FR-21 ======
const filterForm = ref({ spicy: '', cuisine: '', maxCal: null, cookMethod: '' })

const spicyOptions = [
  { value: 'none', label: '不辣' },
  { value: 'low', label: '微辣' },
  { value: 'medium', label: '中辣' },
  { value: 'high', label: '重辣' },
]

// ====== 食材识别（拍照/上传 → Qwen 识别 → 库匹配 → AI 建议） ======
const ingInput = ref(null)
const ingLoading = ref(false)
const recognizedIngredients = ref([])
const recognizedSeasonings = ref([])
const suggestLoading = ref(false)
const ingSuggestion = ref(null)

function triggerIngUpload() {
  if (ingInput.value) ingInput.value.click()
}

function onIngredientUpload(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = async () => {
    const dataUrl = reader.result
    const base64 = dataUrl.split(',')[1] || dataUrl
    ingLoading.value = true
    ingSuggestion.value = null
    try {
      const res = await recognizeIngredients(base64)
      if (!res.success) {
        alert(res.error || '识别失败')
        recognizedIngredients.value = []
        recognizedSeasonings.value = []
      } else {
        recognizedIngredients.value = res.ingredients || []
        recognizedSeasonings.value = res.seasonings || []
      }
    } catch (err) {
      alert('识别失败：' + (err.message || '请重试'))
      recognizedIngredients.value = []
    } finally {
      ingLoading.value = false
      if (ingInput.value) ingInput.value.value = ''
    }
  }
  reader.readAsDataURL(file)
}

function removeIngredient(i) {
  recognizedIngredients.value.splice(i, 1)
}
function removeSeasoning(i) {
  recognizedSeasonings.value.splice(i, 1)
}
function resetIngredient() {
  recognizedIngredients.value = []
  recognizedSeasonings.value = []
  ingSuggestion.value = null
}

async function getSuggestionFromImage() {
  if (!recognizedIngredients.value.length) return alert('请先识别出食材')
  suggestLoading.value = true
  ingSuggestion.value = null
  try {
    const res = await suggestRecipe({
      ingredients: recognizedIngredients.value,
      seasonings: recognizedSeasonings.value,
      forceAi: true,
    })
    ingSuggestion.value = res
  } catch (err) {
    alert('获取建议失败：' + (err.message || '请重试'))
  } finally {
    suggestLoading.value = false
  }
}

// ====== 转盘 FR-22 ======
const customFoodInput = ref('')
const wheelItems = ref([])
const wheelResult = ref(null)
const customCount = ref(0)

function addCustomFood() {
  const name = customFoodInput.value.trim()
  if (!name) return
  wheelItems.value.push({ label: name, color: '#D9A15B' })
  customCount.value++
  customFoodInput.value = ''
}

function removeWheelItem(idx) {
  // 移除自定义项时减少 customCount
  const item = wheelItems.value[idx]
  if (item.color === '#D9A15B') customCount.value--
  wheelItems.value.splice(idx, 1)
  wheelResult.value = null
}

function loadFoodsToWheel() {
  wheelResult.value = null
  customCount.value = 0
  wheelItems.value = foods.value.slice(0, 10).map(f => ({
    label: f.name,
    id: f.id,
    color: undefined, // 使用默认颜色
  }))
}

function clearWheel() {
  wheelItems.value = []
  wheelResult.value = null
  customCount.value = 0
}

// ====== 附近美食 FR-24 ======
const router = useRouter()
function goDetail(food) {
  // 有食谱数据 → 统一跳广场食谱详情页（含食材/步骤/评论/收藏）
  if (food.recipe_id) {
    router.push('/square/' + food.recipe_id)
  } else {
    router.push({ path: '/food/' + food.id, query: { cat: food.category_name || '' } })
  }
}

const nearbyCity = ref('')
const nearbyLoading = ref(false)
const nearbyResult = ref('')
const manualCityMode = ref(false)
const nearbyCityInput = ref('')

// HTML5 精准定位（GPS/WiFi/基站）→ 高德逆地理编码得到城市；失败/拒绝返回空
function geoLocate() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve('')
      return
    }
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { longitude, latitude } = pos.coords
          const r = await fetch(
            `https://restapi.amap.com/v3/geocode/regeo?location=${longitude},${latitude}&key=38b348fb67f2d42cb1fa0fe61301bc45`,
            { signal: AbortSignal.timeout(5000) }
          )
          if (!r.ok) {
            resolve('')
            return
          }
          const d = await r.json()
          const comp = d.regeocode?.addressComponent
          const city = comp?.city || comp?.province || ''
          resolve(String(city).replace(/市$|省$/, '') || '')
        } catch {
          resolve('')
        }
      },
      () => resolve(''),  // 用户拒绝/超时 → 回退 IP
      { timeout: 8000, maximumAge: 60000 }
    )
  })
}

// 高德 JS SDK 动态加载（复用现有 key）
let _amapReady = null
function loadAMapScript() {
  if (window.AMap) return Promise.resolve()
  if (!_amapReady) {
    _amapReady = new Promise((resolve, reject) => {
      const s = document.createElement('script')
      s.src = 'https://webapi.amap.com/maps?v=2.0&key=38b348fb67f2d42cb1fa0fe61301bc45&plugin=AMap.Geolocation'
      s.onload = () => setTimeout(() => (window.AMap ? resolve() : reject(new Error('AMap 未就绪'))), 500)
      s.onerror = () => reject(new Error('高德 SDK 加载失败'))
      document.head.appendChild(s)
    })
  }
  return _amapReady
}

// 高德 JS SDK Geolocation 兜底（HTML5 被拒/失败时，由高德封装处理）
function amapLocate() {
  return new Promise((resolve) => {
    loadAMapScript()
      .then(() => {
        const geolocation = new window.AMap.Geolocation({
          enableHighAccuracy: false,
          timeout: 8000,
          zoomToAccuracy: false,
        })
        geolocation.getCurrentPosition((status, result) => {
          if (status === 'complete' && result?.addressComponent) {
            const city = result.addressComponent.city || result.addressComponent.province || ''
            resolve(String(city).replace(/市$|省$/, '') || '')
          } else {
            resolve('')
          }
        })
      })
      .catch(() => resolve(''))
    setTimeout(() => resolve(''), 12000)  // 总兜底超时
  })
}

// 页面加载时：① HTML5 精准 → ② 高德 JS SDK → ③ IP 链
onMounted(async () => {
  const html5City = await geoLocate()
  if (html5City) {
    nearbyCity.value = html5City
    return
  }
  const amapCity = await amapLocate()
  if (amapCity) {
    nearbyCity.value = amapCity
    return
  }
  const geoAPIs = [
    // 高德 IP 定位 — 返回纯中文城市名
    async () => {
      const r = await fetch(
        'https://restapi.amap.com/v3/ip?key=38b348fb67f2d42cb1fa0fe61301bc45',
        { signal: AbortSignal.timeout(5000) }
      )
      if (!r.ok) throw new Error('fail')
      const d = await r.json()
      const adcode = String(d.adcode || '')
      // 高德只定位到省级（adcode 后两位为 00）时，city 是默认省会，改用省名避免误导
      if (adcode.endsWith('00') && d.province) {
        return (d.province || '').replace(/市$|省$/, '')
      }
      const city = (d.city || d.province || '').replace(/市$|省$/, '')
      return city || ''
    },
    // api.ip.sb — 英文/拼音，仅作为备选
    async () => {
      const r = await fetch('https://api.ip.sb/geoip', { signal: AbortSignal.timeout(5000) })
      if (!r.ok) throw new Error('fail')
      const d = await r.json()
      return d.city || d.region || d.country || ''
    },
    // api.vore.top — 备选
    async () => {
      const r = await fetch('https://api.vore.top/api/IPdata', { signal: AbortSignal.timeout(5000) })
      if (!r.ok) throw new Error('fail')
      const d = await r.json()
      return (d.adcode?.o || d.ipdata?.city || '')
    },
  ]

  for (const fn of geoAPIs) {
    try {
      const city = await fn()
      if (city) {
        nearbyCity.value = city
        break
      }
    } catch { /* 尝试下一个 */ }
  }
})

function setManualCity() {
  const c = nearbyCityInput.value.trim()
  if (c) {
    nearbyCity.value = c
    manualCityMode.value = false
  }
}

async function getNearbyRecommend() {
  nearbyLoading.value = true
  nearbyResult.value = ''

  const token = localStorage.getItem('token')
  if (!token) {
    nearbyResult.value = '请先登录。'
    nearbyLoading.value = false
    return
  }

  const city = nearbyCity.value || '当前城市'
  const prompt = `我在${city}，请推荐3道当地特色菜，每道菜一行，格式：菜名 — 一句话理由。总共不超过100字。`

  try {
    const resp = await fetch('/api/chat/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ content: prompt, session_id: 'today-nearby' }),
    })

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: '请求失败' }))
      nearbyResult.value = err.detail || '查询失败'
      nearbyLoading.value = false
      return
    }

    // SSE 流式读取（event: / data: 两行配对）
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''
    let fullText = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (currentEvent === 'token') {
              fullText += data.content
              nearbyResult.value = fullText
            }
          } catch { /* skip */ }
          currentEvent = ''
        }
      }
    }

    if (!nearbyResult.value) nearbyResult.value = fullText || '暂无结果，请稍后再试。'
  } catch {
    nearbyResult.value = '网络错误，请检查后端是否启动。'
  } finally {
    nearbyLoading.value = false
  }
}

function onWheelDone(item) {
  wheelResult.value = item
}

function searchWheelResult() {
  if (!wheelResult.value) return
  tab.value = 'search'
  keyword.value = wheelResult.value.label
  nextTick(() => search())
}

// ====== 搜索 & 分类 ======
onMounted(async () => {
  try {
    const res = await axios.get('/api/foods/categories')
    categories.value = res.data
    allCuisineOptions.value = res.data.map(c => c.name)
  } catch { /* ignore */ }
  search()
})

async function search() {
  loading.value = true
  // 普通搜索/分类筛选会退出快捷筛选模式（DIY 筛选除外）
  if (selectedCat.value !== customCatId.value) viewMode.value = 'all'
  try {
    const params = { page_size: 50 }
    if (keyword.value) params.keyword = keyword.value
    if (selectedCat.value) params.category_id = selectedCat.value
    if (filterForm.value.cuisine) params.cuisine = filterForm.value.cuisine
    const res = await axios.get('/api/foods', { params })
    let items = res.data.items || []

    if (filterForm.value.spicy) {
      items = items.filter(f => {
        try {
          const tags = typeof f.tags === 'string' ? JSON.parse(f.tags) : (f.tags || {})
          return tags.spicy === filterForm.value.spicy
        } catch { return true }
      })
    }
    if (filterForm.value.maxCal) {
      items = items.filter(f => (f.calories_per_100g || 9999) <= filterForm.value.maxCal)
    }
    if (filterForm.value.cookMethod) {
      items = items.filter(f => {
        try {
          const tags = typeof f.tags === 'string' ? JSON.parse(f.tags) : (f.tags || {})
          return tags.cook_method === filterForm.value.cookMethod
        } catch { return true }
      })
    }

    foods.value = items
  } catch {
    foods.value = []
  } finally {
    loading.value = false
  }
}

function selectCategory(id) {
  selectedCat.value = id === selectedCat.value ? null : id
  viewMode.value = selectedCat.value === customCatId.value ? 'diy' : 'all'
  search()
}

// 「只看我的 DIY 菜谱」独立快捷筛选
const customCatId = computed(() => {
  const c = categories.value.find(c => c.name === '自定义')
  return c ? c.id : null
})
const normalCategories = computed(() => categories.value.filter(c => c.name !== '自定义'))

function toggleCustom() {
  if (!customCatId.value) return
  selectedCat.value = selectedCat.value === customCatId.value ? null : customCatId.value
  viewMode.value = selectedCat.value === customCatId.value ? 'diy' : 'all'
  search()
}

// 「我收藏的食谱」快捷筛选
async function toggleFav() {
  if (viewMode.value === 'fav') {
    viewMode.value = 'all'
    search()
    return
  }
  viewMode.value = 'fav'
  loading.value = true
  try {
    const res = await getFavoriteRecipes()
    foods.value = res.items || []
  } catch {
    foods.value = []
  } finally {
    loading.value = false
  }
}

function applyFilterFromDecide() {
  tab.value = 'search'
  search()
}

// ====== 饮食记录 ======
const showModal = ref(false)
const selectedFood = ref(null)
const recording = ref(false)
const recordMsg = ref('')
const recordOk = ref(false)

const mealOptions = [
  { value: 'breakfast', label: '早餐' },
  { value: 'lunch', label: '午餐' },
  { value: 'dinner', label: '晚餐' },
  { value: 'snack', label: '零食' },
]

const recordForm = ref({ meal_type: 'lunch', quantity_g: 200 })

const estimatedCal = computed(() => {
  if (!selectedFood.value) return 0
  const cal = selectedFood.value.calories_per_100g || 0
  return Math.round(cal * recordForm.value.quantity_g / 100)
})

const canRecord = computed(() => recordForm.value.quantity_g >= 10 && recordForm.value.meal_type)

function openRecordModal(food) {
  selectedFood.value = food
  recordForm.value = { meal_type: 'lunch', quantity_g: 200 }
  recordMsg.value = ''
  recordOk.value = false
  showModal.value = true
}

async function submitRecord() {
  if (!canRecord.value || !selectedFood.value) return
  recording.value = true
  recordMsg.value = ''
  try {
    await createDietRecord({
      food_id: selectedFood.value.id,
      meal_type: recordForm.value.meal_type,
      quantity_g: recordForm.value.quantity_g,
    })
    recordMsg.value = `已记录：${selectedFood.value.name} ${recordForm.value.quantity_g}g`
    recordOk.value = true
    setTimeout(() => { showModal.value = false }, 1500)
  } catch (e) {
    recordMsg.value = e?.message || '记录失败，请重试'
    recordOk.value = false
  } finally {
    recording.value = false
  }
}
</script>

<style scoped>
/* ====== Tab 栏 ====== */
.tab-bar {
  display: flex;
  gap: 0;
  margin-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-divider);
}
.tab-btn {
  padding: 10px 24px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  font-size: 15px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
}
.tab-btn.active {
  color: var(--color-primary-dark);
  border-bottom-color: var(--color-primary);
}
.tab-btn:hover:not(.active) {
  color: var(--color-text);
}

/* ====== 搜索栏 ====== */
.search-bar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}
.search-bar .input { flex: 1; }
.filter-tags {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-md);
}
.food-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--spacing-md);
}
/* ====== 食材识别卡片 ====== */
.ing-chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.ing-chip {
  cursor: pointer;
}
.matched-recipe {
  padding: 6px 10px;
  background: var(--color-bg-warm);
  border-radius: 6px;
  margin-bottom: 6px;
}
.ai-suggestion-box {
  margin-top: 10px;
  padding: 12px;
  background: var(--color-bg-warm);
  border-left: 3px solid var(--color-primary);
  border-radius: 6px;
}
.custom-filter-bar {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}
.custom-btn {
  flex: 1;
}
.food-card {
  cursor: default;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.food-card.can-click {
  cursor: pointer;
}
.food-card.can-click:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}
.food-card-img {
  height: 120px;
  background: var(--color-bg-warm);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
}
.food-card-body { padding: var(--spacing-md); }
.food-card-body h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 2px;
}
.food-card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-sm);
}
.btn-sm { padding: 6px 14px; font-size: 13px; }

/* ====== 辅助决策布局（上下三个独立卡片） ====== */
.decide-stack {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}
.decide-card {
  padding: var(--spacing-md) var(--spacing-lg);
}
.decide-card-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text);
}

/* ====== 表单增强 ====== */
.form-group { margin-top: var(--spacing-md); }
.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 4px;
  color: var(--color-text-secondary);
}
.input-sm { padding: 6px 10px; font-size: 13px; }
.meal-btns { display: flex; gap: var(--spacing-sm); flex-wrap: wrap; }
.tag-sm { padding: 4px 10px; font-size: 12px; }
.range-row { display: flex; align-items: center; gap: var(--spacing-sm); }

/* ====== 转盘 ====== */
.wheel-add-row {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}
.wheel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: var(--spacing-sm);
  justify-content: center;
}
.tag-warm {
  background: #FFF3E0;
  color: var(--color-primary-dark);
  border-color: var(--color-primary-light);
}
.wheel-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
}

/* ====== AI 结果 ====== */
.ai-result-card {
  margin-top: var(--spacing-md);
  padding: var(--spacing-sm);
  background: var(--color-bg-warm);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-primary);
}
.ai-result-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--color-text);
  white-space: pre-wrap;
}

/* ====== 弹窗 ====== */
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
.modal-content h3 { margin-bottom: 4px; font-size: var(--font-size-lg); }
.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: flex-end;
  margin-top: var(--spacing-lg);
}

@media (max-width: 640px) {
  .food-grid { grid-template-columns: 1fr 1fr; }
}
</style>
