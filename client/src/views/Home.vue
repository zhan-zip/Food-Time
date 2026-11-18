<template>
  <div class="page-home">
    <!-- Hero：全屏暖色渐变 + 本地美食背景（视觉来自静态演示稿） -->
    <section class="hero-section">
      <div class="site-badge">食光研究所</div>

      <div class="hero-content">
        <h1 class="hero-title">食光记</h1>
        <p class="hero-subtitle">真正的美食能让人感受到幸福</p>

        <div class="search-container">
          <div v-if="!searchOpen" class="search-lines" @click="openSearch">
            <span class="line"></span>
            <span class="line"></span>
            <span class="line"></span>
          </div>

          <div v-else class="search-box active">
            <span class="search-icon">🔍</span>
            <input
              ref="searchInputRef"
              v-model="searchKw"
              class="search-input"
              placeholder="搜寻标题、描述或标签..."
              @keyup.enter="doSearch"
              @blur="onSearchBlur"
            />
            <button class="search-clear" @mousedown.prevent="clearSearch">✕</button>
          </div>
        </div>
      </div>
    </section>

    <!-- 三栏布局：品牌卡 / 精选轮播 / 音乐播放器 -->
    <section class="three-columns-section">
      <div class="container-wide">
        <div class="three-columns">
          <!-- 左栏：品牌介绍 -->
          <div class="column-left">
            <div class="intro-card">
              <div class="intro-avatar"><span class="intro-avatar-emoji">🍜</span></div>
              <h3 class="intro-title">食光记</h3>
              <p class="intro-desc">
                以食为光，记录每一餐的温度。AI 为你推荐、识别、记账与规划，让每一个「今天吃什么」都有答案。
              </p>
            </div>
          </div>

          <!-- 中栏：精选菜谱轮播（广场最新数据） -->
          <div class="column-center">
            <div v-if="recipes.length" class="content-carousel">
              <router-link class="featured-card" :to="'/square/' + currentRecipe.id">
                <div class="featured-image">
                  <FoodImage :name="currentRecipe.name" />
                  <div class="carousel-dots">
                    <span
                      v-for="(r, i) in recipes"
                      :key="r.id"
                      class="dot"
                      :class="{ active: i === carouselIndex }"
                      @click.prevent="carouselIndex = i"
                    ></span>
                  </div>
                </div>
                <div class="featured-info">
                  <h3>{{ currentRecipe.name }}</h3>
                  <p class="featured-meta">
                    <span>{{ currentRecipe.cuisine || '家常' }}</span>
                    · ❤️{{ currentRecipe.like_count || 0 }}
                  </p>
                </div>
              </router-link>
            </div>
            <div v-else class="content-carousel">
              <div class="featured-card">
                <div class="featured-image featured-empty">🍲</div>
                <div class="featured-info">
                  <h3>暂无精选</h3>
                  <p class="featured-meta">去广场分享你的第一道菜吧</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 右栏：本地音乐播放器（bgm 预加载自 /static/audio） -->
          <div class="column-right">
            <div class="music-player-card">
              <div class="player-header">
                <div class="player-label">CLOUD MUSIC</div>
                <div class="player-cover"><span class="player-cover-emoji">🎵</span></div>
                <div class="player-track-name">{{ playlist[trackIndex].name }}</div>
                <div class="player-artist">{{ playlist[trackIndex].artist }}</div>
              </div>

              <div class="player-progress">
                <span class="progress-time">{{ formatTime(currentTime) }}</span>
                <div class="progress-bar" ref="progressBarRef" @click="seek">
                  <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
                </div>
                <span class="progress-time">{{ formatTime(duration) }}</span>
              </div>

              <div class="player-buttons">
                <button class="player-btn" @click="prevTrack">⏮</button>
                <button class="player-btn player-btn-play" @click="togglePlay">
                  <span>{{ isPlaying ? '⏸' : '▶️' }}</span>
                </button>
                <button class="player-btn" @click="nextTrack">⏭</button>
                <button class="player-btn" @click="toggleMute">
                  <span>{{ isMuted ? '🔇' : '🔊' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <audio ref="audioRef" preload="none"></audio>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getRecipes } from '../api/public'
import FoodImage from '../components/FoodImage.vue'
import { maybeStartOnboarding } from '../utils/onboarding'

const router = useRouter()

// ====== Hero 搜索：三横线点击展开，回车跳转「今天吃什么」并带关键词 ======
const searchOpen = ref(false)
const searchKw = ref('')
const searchInputRef = ref(null)

function openSearch() {
  searchOpen.value = true
  nextTick(() => searchInputRef.value?.focus())
}

function onSearchBlur() {
  setTimeout(() => {
    if (!searchKw.value) searchOpen.value = false
  }, 200)
}

function clearSearch() {
  searchKw.value = ''
  searchOpen.value = false
}

function doSearch() {
  const kw = searchKw.value.trim()
  if (!kw) return
  router.push({ path: '/today-eat', query: { keyword: kw } })
}

// ====== 中栏轮播：广场最新 3 个菜谱，7 秒自动轮播 ======
const recipes = ref([])
const carouselIndex = ref(0)
const currentRecipe = computed(() => recipes.value[carouselIndex.value] || {})
let carouselTimer = null

onMounted(async () => {
  try {
    const res = await getRecipes(1, 3, { sort_by: 'time', order: 'desc' })
    recipes.value = res.items || []
    if (recipes.value.length > 1) {
      carouselTimer = setInterval(() => {
        carouselIndex.value = (carouselIndex.value + 1) % recipes.value.length
      }, 7000)
    }
  } catch (e) {
    console.error('加载推荐失败', e)
  }

  // 音乐播放器初始化
  audio.value = audioRef.value
  audio.value.src = playlist[trackIndex.value].url
  audio.value.volume = 0.5
  audio.value.addEventListener('timeupdate', onTimeUpdate)
  audio.value.addEventListener('loadedmetadata', onLoadedMetadata)
  audio.value.addEventListener('ended', nextTrack)

  // 新用户首次登录：触发引导（等 DOM 渲染完，导航元素已就绪）
  nextTick(() => maybeStartOnboarding())
})

onBeforeUnmount(() => {
  if (carouselTimer) clearInterval(carouselTimer)
  if (audio.value) {
    audio.value.pause()
    audio.value.removeEventListener('timeupdate', onTimeUpdate)
    audio.value.removeEventListener('loadedmetadata', onLoadedMetadata)
    audio.value.removeEventListener('ended', nextTrack)
  }
})

// ====== 右栏：本地音乐播放器（音频在 server/static/audio，断网可用） ======
const playlist = [
  { name: '神探', artist: '丁世光', url: '/static/audio/bgm-1.mp3' },
  { name: '晴天', artist: '周杰伦', url: '/static/audio/bgm-2.mp3' },
  { name: '夜曲', artist: '周杰伦', url: '/static/audio/bgm-3.mp3' },
]
const audioRef = ref(null)
let audio = ref(null)
const trackIndex = ref(0)
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const progressBarRef = ref(null)

const progressPercent = computed(() =>
  duration.value ? (currentTime.value / duration.value) * 100 : 0
)

function onTimeUpdate() {
  currentTime.value = audio.value.currentTime || 0
}

function onLoadedMetadata() {
  duration.value = audio.value.duration || 0
}

function togglePlay() {
  if (isPlaying.value) {
    audio.value.pause()
  } else {
    audio.value.play()
  }
  isPlaying.value = !isPlaying.value
}

function loadTrack() {
  const track = playlist[trackIndex.value]
  audio.value.src = track.url
  currentTime.value = 0
  duration.value = 0
  if (isPlaying.value) audio.value.play()
}

function prevTrack() {
  trackIndex.value = (trackIndex.value - 1 + playlist.length) % playlist.length
  loadTrack()
}

function nextTrack() {
  trackIndex.value = (trackIndex.value + 1) % playlist.length
  loadTrack()
}

function toggleMute() {
  isMuted.value = !isMuted.value
  audio.value.muted = isMuted.value
}

function seek(e) {
  if (!duration.value) return
  const rect = progressBarRef.value.getBoundingClientRect()
  const percent = (e.clientX - rect.left) / rect.width
  audio.value.currentTime = percent * audio.value.duration
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}
</script>

<style scoped>
/* ===== Hero：全屏暖色渐变 + 本地美食背景 ===== */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    linear-gradient(
      135deg,
      rgba(250, 245, 239, 0.95) 0%,
      rgba(245, 230, 211, 0.92) 50%,
      rgba(249, 223, 192, 0.95) 100%
    ),
    url('/static/hero-dish.png') center/cover no-repeat;
}

.site-badge {
  position: absolute;
  top: 76px;
  left: 80px;
  font-size: 13px;
  color: #8B7355;
  letter-spacing: 2px;
  font-weight: 400;
  opacity: 0.85;
  font-family: "KaiTi", "STKaiti", serif;
}

.hero-content {
  position: relative;
  z-index: 10;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 80px;
}

.hero-title {
  font-family: "STKaiti", "KaiTi", "楷体", "Songti SC", cursive, serif;
  font-size: clamp(64px, 12vw, 140px);
  font-weight: 500;
  color: #2D1B10;
  line-height: 1;
  letter-spacing: 0.12em;
  text-shadow:
    2px 2px 0px rgba(217, 161, 91, 0.3),
    4px 4px 8px rgba(217, 161, 91, 0.2);
  animation: fadeInUp 1s ease-out;
  margin-bottom: 24px;
  font-style: italic;
  background: linear-gradient(135deg, #2D1B10 0%, #8B4513 50%, #D9A15B 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-family: "Songti SC", "SimSun", "STSong", Georgia, serif;
  font-size: clamp(18px, 2.5vw, 24px);
  color: rgba(45, 27, 16, 0.75);
  line-height: 1.8;
  letter-spacing: 0.08em;
  animation: fadeInUp 1s ease-out 0.2s both;
}

/* 三横线 → 展开搜索框 */
.search-container {
  animation: fadeInUp 1s ease-out 0.4s both;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 40px;
}

.search-lines {
  display: flex;
  flex-direction: column;
  gap: 8px;
  cursor: pointer;
  padding: 16px 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-lines:hover {
  transform: scale(1.1);
}

.search-lines .line {
  width: 40px;
  height: 3px;
  background: rgba(45, 27, 16, 0.4);
  border-radius: 2px;
  transition: all 0.3s ease;
}

.search-lines:hover .line {
  background: rgba(217, 161, 91, 0.8);
}

.search-lines .line:nth-child(2) {
  width: 32px;
}

.search-box {
  position: relative;
  width: 400px;
  max-width: 90vw;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(217, 161, 91, 0.3);
  border-radius: 50px;
  padding: 4px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 12px 48px rgba(217, 161, 91, 0.2);
  animation: expandSearch 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes expandSearch {
  from {
    width: 50px;
    opacity: 0;
  }
  to {
    width: 400px;
    opacity: 1;
  }
}

.search-icon {
  font-size: 20px;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  color: #2D1B10;
  padding: 14px 0;
  outline: none;
}

.search-input::placeholder {
  color: rgba(45, 27, 16, 0.4);
}

.search-clear {
  background: transparent;
  border: none;
  color: rgba(45, 27, 16, 0.5);
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s;
}

.search-clear:hover {
  color: rgba(45, 27, 16, 0.8);
}

/* ===== 三栏布局 ===== */
.three-columns-section {
  padding: 80px 0;
  background: linear-gradient(
    180deg,
    rgba(255, 248, 240, 0.95) 0%,
    rgba(250, 245, 239, 0.97) 100%
  );
}

.container-wide {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 40px;
}

.three-columns {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 32px;
  align-items: stretch;
}

/* 左栏：品牌卡 */
.intro-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px 24px;
  box-shadow: 0 8px 32px rgba(217, 161, 91, 0.12);
  border: 1px solid rgba(217, 161, 91, 0.2);
  text-align: center;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.intro-avatar {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #D9A15B 0%, #FFB85C 100%);
  box-shadow: 0 4px 16px rgba(217, 161, 91, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.intro-avatar-emoji {
  font-size: 40px;
  line-height: 1;
}

.intro-title {
  font-family: "STKaiti", "KaiTi", "楷体", serif;
  font-size: 24px;
  font-weight: 600;
  color: #2D1B10;
  margin-bottom: 16px;
  letter-spacing: 0.05em;
}

.intro-desc {
  font-size: 14px;
  line-height: 1.8;
  color: rgba(45, 27, 16, 0.7);
  letter-spacing: 0.02em;
}

/* 中栏：轮播卡 */
.content-carousel {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 8px 32px rgba(217, 161, 91, 0.12);
  border: 1px solid rgba(217, 161, 91, 0.2);
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.featured-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
  height: 100%;
  transition: transform 0.3s ease;
}

.featured-card:hover {
  transform: scale(1.02);
}

.featured-image {
  position: relative;
  width: 100%;
  height: 400px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(217, 161, 91, 0.1) 0%, rgba(255, 200, 124, 0.1) 100%);
}

.featured-image :deep(.food-img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.featured-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 72px;
}

.carousel-dots {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.carousel-dots .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 1px 4px rgba(45, 27, 16, 0.3);
}

.carousel-dots .dot.active {
  width: 24px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.9);
}

.featured-info {
  padding: 24px 32px;
  background: rgba(255, 255, 255, 0.95);
}

.featured-info h3 {
  font-size: 24px;
  font-weight: 600;
  color: #2D1B10;
  margin-bottom: 8px;
}

.featured-meta {
  font-size: 14px;
  color: rgba(45, 27, 16, 0.6);
}

/* 右栏：音乐播放器 */
.music-player-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(217, 161, 91, 0.12);
  border: 1px solid rgba(217, 161, 91, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.player-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}

.player-label {
  font-size: 10px;
  font-weight: 600;
  color: rgba(45, 27, 16, 0.5);
  letter-spacing: 0.15em;
}

.player-cover {
  width: 160px;
  height: 160px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, #D9A15B 0%, #FFB85C 100%);
  box-shadow: 0 8px 24px rgba(217, 161, 91, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.player-cover-emoji {
  font-size: 72px;
  line-height: 1;
}

.player-track-name {
  font-size: 16px;
  font-weight: 600;
  color: #2D1B10;
  text-align: center;
  margin-top: 8px;
}

.player-artist {
  font-size: 14px;
  color: rgba(45, 27, 16, 0.6);
  text-align: center;
}

.player-progress {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}

.progress-time {
  font-size: 11px;
  color: rgba(45, 27, 16, 0.5);
  font-variant-numeric: tabular-nums;
  min-width: 38px;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(217, 161, 91, 0.2);
  border-radius: 2px;
  cursor: pointer;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #D9A15B 0%, #FFB85C 100%);
  border-radius: 2px;
  width: 0%;
  transition: width 0.1s linear;
}

.player-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.player-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: #2D1B10;
  font-size: 18px;
}

.player-btn:hover {
  background: rgba(217, 161, 91, 0.1);
}

.player-btn-play {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #D9A15B 0%, #FFB85C 100%);
  color: white;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(217, 161, 91, 0.3);
}

.player-btn-play:hover {
  background: linear-gradient(135deg, #C8904A 0%, #EEA74B 100%);
  transform: scale(1.05);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ===== 响应式 ===== */
@media (max-width: 1024px) {
  .three-columns {
    grid-template-columns: 1fr 300px;
  }

  .column-left {
    grid-column: 1 / -1;
  }
}

@media (max-width: 768px) {
  .hero-content {
    padding: 0 20px;
  }

  .hero-title {
    font-size: 48px;
  }

  .site-badge {
    top: 64px;
    left: 20px;
  }

  .three-columns {
    grid-template-columns: 1fr;
  }

  .featured-image {
    height: 280px;
  }
}
</style>
