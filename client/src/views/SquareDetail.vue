<template>
  <div class="page container page-section">
    <!-- 加载中 -->
    <div v-if="loading" class="text-center" style="padding: 60px 0;">
      <p>加载中...</p>
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="text-center" style="padding: 60px 0;">
      <p class="text-secondary">{{ error }}</p>
      <button class="btn btn-ghost" @click="$router.back()" style="margin-top: var(--spacing-lg);">&larr; 返回广场</button>
    </div>

    <!-- 食谱详情 -->
    <template v-else>
      <button class="btn btn-ghost" @click="$router.back()" style="margin-bottom: var(--spacing-lg);">&larr; 返回广场</button>

      <div class="detail-layout">
        <!-- 左侧图片区 -->
        <div class="detail-sidebar">
          <div class="detail-img" v-if="recipe.image_url">
            <img :src="recipe.image_url" :alt="recipe.name" />
          </div>
          <div class="detail-img placeholder" v-else>&#x1F372;</div>

          <!-- 营养数据 -->
          <div class="nutrition-card" v-if="recipe.calories">
            <h4>营养成分（每100g）</h4>
            <div class="nutrition-grid">
              <div class="nutrition-item"><span>热量</span><strong>{{ recipe.calories }}kcal</strong></div>
              <div class="nutrition-item"><span>蛋白质</span><strong>{{ recipe.protein || '-' }}g</strong></div>
              <div class="nutrition-item"><span>脂肪</span><strong>{{ recipe.fat || '-' }}g</strong></div>
              <div class="nutrition-item"><span>碳水</span><strong>{{ recipe.carbs || '-' }}g</strong></div>
            </div>
          </div>

          <!-- 收藏按钮 -->
          <button
            class="btn save-btn"
            :class="saved ? 'btn-ghost' : 'btn-primary'"
            @click="toggleSave"
            :disabled="savingAction"
          >
            {{ saved ? '&#x2764; 已添加到我的食物库' : '+ 添加到我的食物库' }}
          </button>
        </div>

        <!-- 右侧内容区 -->
        <div class="detail-body">
          <h1 class="detail-title">{{ recipe.name }}</h1>

          <div class="detail-meta">
            <span class="text-secondary">by <strong>{{ recipe.author }}</strong></span>
            <span class="detail-date text-muted">{{ formatDate(recipe.created_at) }}</span>
          </div>

          <!-- 标签 -->
          <div class="detail-tags" v-if="recipe.tags || recipe.cuisine">
            <span v-if="recipe.cuisine" class="tag tag-primary">{{ recipe.cuisine }}</span>
            <span v-if="recipe.category" class="tag tag-default">{{ recipe.category }}</span>
            <span v-if="tags.spicy" class="tag tag-default">辣度: {{ spicyLabel(tags.spicy) }}</span>
            <span v-if="tags.level" class="tag tag-default">难度: {{ levelLabel(tags.level) }}</span>
          </div>

          <!-- 简介 -->
          <div class="detail-section" v-if="recipe.description">
            <h3>食物简介</h3>
            <p class="detail-desc">{{ recipe.description }}</p>
          </div>

          <!-- 材料 -->
          <div class="detail-section" v-if="recipe.materials && recipe.materials.length">
            <h3>食材</h3>
            <div class="ingredient-list">
              <span v-for="m in recipe.materials" :key="m.name" class="ingredient-tag">
                {{ m.name }} <small v-if="m.quantity">({{ m.quantity }})</small>
              </span>
            </div>
          </div>

          <!-- 调料 -->
          <div class="detail-section" v-if="recipe.seasonings && recipe.seasonings.length">
            <h3>调料</h3>
            <div class="ingredient-list">
              <span v-for="s in recipe.seasonings" :key="s.name" class="ingredient-tag seasoning">
                {{ s.name }} <small v-if="s.quantity">({{ s.quantity }})</small>
              </span>
            </div>
          </div>

          <!-- 做法 -->
          <div class="detail-section" v-if="recipe.steps && recipe.steps.length">
            <h3>做法</h3>
            <ol class="steps-list">
              <li v-for="(step, idx) in recipe.steps" :key="idx">{{ step }}</li>
            </ol>
          </div>

          <!-- 统计 -->
          <div class="detail-stats text-sm text-muted" v-if="recipe.like_count !== undefined">
            <span>&#x2764; {{ recipe.like_count }} 点赞</span>
            <span>&#x2B50; {{ recipe.fav_count }} 收藏</span>
            <span>&#x1F4AC; {{ recipe.comment_count }} 评论</span>
          </div>

          <hr class="divider" />

          <!-- 评论区 -->
          <h3>评论区 ({{ comments.length }})</h3>

          <div v-if="!token" class="text-muted text-sm" style="margin: var(--spacing-md) 0;">
            请先登录后发表评论
          </div>

          <div v-else class="comment-form">
            <textarea
              v-model="commentText"
              class="input"
              rows="3"
              placeholder="写下你的评论..."
              :disabled="commenting"
            ></textarea>
            <button
              class="btn btn-primary btn-sm"
              @click="submitComment"
              :disabled="!commentText.trim() || commenting"
              style="margin-top: var(--spacing-sm);"
            >
              {{ commenting ? '发送中...' : '发表评论' }}
            </button>
          </div>

          <div class="comment-list" v-if="comments.length > 0">
            <div v-for="c in comments" :key="c.id" class="comment-item">
              <div class="comment-header">
                <strong>{{ c.user }}</strong>
                <span class="text-muted text-xs">{{ formatDate(c.created_at) }}</span>
              </div>
              <p class="comment-content">{{ c.content }}</p>
            </div>
          </div>
          <p v-else class="text-muted text-sm" style="margin-top: var(--spacing-md);">
            暂无评论，抢个沙发吧
          </p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getRecipeDetail, getComments, addComment, saveRecipe, unsaveRecipe } from '../api/public'

const route = useRoute()
const recipe = ref({})
const comments = ref([])
const loading = ref(true)
const error = ref('')
const saved = ref(false)
const savingAction = ref(false)
const commentText = ref('')
const commenting = ref(false)

const token = localStorage.getItem('token')

const tags = computed(() => {
  const t = recipe.value.tags
  if (!t) return {}
  if (typeof t === 'string') {
    try { return JSON.parse(t) } catch { return {} }
  }
  return t
})

const spicyLabel = (v) => ({ high: '麻辣', medium: '中辣', low: '微辣', none: '不辣' }[v] || v)
const levelLabel = (v) => ({ entry: '入门', medium: '中等', hard: '困难' }[v] || v)

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

async function fetchDetail() {
  loading.value = true
  error.value = ''
  try {
    const id = route.params.id
    const res = await getRecipeDetail(id)
    recipe.value = res
    await fetchComments()
  } catch (e) {
    const msg = e.message
    error.value = msg === '食谱不存在' ? '该食谱不存在或已被删除' : '加载失败：' + msg
  } finally {
    loading.value = false
  }
}

async function fetchComments() {
  const id = route.params.id
  try {
    const res = await getComments(id)
    comments.value = res.comments || []
  } catch { /* 评论加载失败不影响正文显示 */ }
}

async function toggleSave() {
  if (!token) return alert('请先登录')
  savingAction.value = true
  try {
    if (saved.value) {
      await unsaveRecipe(route.params.id)
      saved.value = false
    } else {
      await saveRecipe(route.params.id)
      saved.value = true
    }
  } catch (e) {
    alert('操作失败：' + (e.message || '请重试'))
  } finally {
    savingAction.value = false
  }
}

async function submitComment() {
  if (!token) return
  const text = commentText.value.trim()
  if (!text) return
  commenting.value = true
  try {
    const res = await addComment(route.params.id, text)
    comments.value.unshift(res)
    commentText.value = ''
    if (recipe.value.comment_count !== undefined) {
      recipe.value.comment_count++
    }
  } catch (e) {
    alert('评论失败：' + (e.response?.data?.detail || e.message))
  } finally {
    commenting.value = false
  }
}

onMounted(fetchDetail)
watch(() => route.params.id, fetchDetail)
</script>

<style scoped>
.detail-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: var(--spacing-xl);
  align-items: start;
}
.detail-sidebar {
  position: sticky;
  top: 80px;
}
.detail-img {
  width: 100%;
  height: 220px;
  border-radius: var(--radius-md);
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.detail-img.placeholder {
  background: var(--color-bg-warm);
  font-size: 64px;
}
.detail-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.nutrition-card {
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-top: var(--spacing-md);
}
.nutrition-card h4 {
  font-size: var(--font-size-sm);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--color-primary-dark);
}
.nutrition-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-sm);
}
.nutrition-item {
  text-align: center;
  padding: var(--spacing-xs);
}
.nutrition-item span {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}
.nutrition-item strong {
  font-size: var(--font-size-base);
  color: var(--color-primary-dark);
}
.save-btn {
  width: 100%;
  margin-top: var(--spacing-md);
  text-align: center;
}

.detail-title {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--spacing-xs);
}
.detail-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.detail-date {
  font-size: var(--font-size-xs);
}
.detail-tags {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  margin-bottom: var(--spacing-lg);
}
.detail-desc {
  line-height: 1.8;
  color: var(--color-text);
}
.detail-section {
  margin-bottom: var(--spacing-lg);
}
.detail-section h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
  color: var(--color-primary-dark);
  padding-left: 8px;
  border-left: 3px solid var(--color-primary);
}
.ingredient-list {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}
.ingredient-tag {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 4px 12px;
  background: rgba(217, 161, 91, 0.08);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text);
}
.ingredient-tag small {
  color: var(--color-text-muted);
}
.ingredient-tag.seasoning {
  background: rgba(122, 166, 105, 0.08);
}
.steps-list {
  padding-left: 20px;
  color: var(--color-text);
}
.steps-list li {
  margin-bottom: var(--spacing-sm);
  line-height: 1.7;
  padding-left: 4px;
}
.detail-stats {
  display: flex;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-md);
}
.detail-stats + hr {
  margin-top: var(--spacing-lg);
}

/* 评论区 */
.comment-form {
  margin: var(--spacing-md) 0 var(--spacing-lg);
}
.comment-form textarea {
  resize: vertical;
  min-height: 80px;
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}
.comment-item {
  padding: var(--spacing-md);
  background: var(--color-bg-warm);
  border-radius: var(--radius-md);
}
.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xs);
}
.comment-content {
  font-size: var(--font-size-sm);
  line-height: 1.6;
  color: var(--color-text);
}

@media (max-width: 768px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
  .detail-sidebar {
    position: static;
    display: flex;
    flex-direction: column;
  }
  .detail-img {
    height: 200px;
  }
}
</style>
