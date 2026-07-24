<template>
  <div style="min-height: 100vh; background: var(--color-bg);">
    <header style="background: var(--color-bg-card); border-bottom: 1px solid var(--color-divider); padding: 16px 0;">
      <div class="container flex justify-between items-center">
        <h2 style="font-size: var(--font-size-lg); font-weight: 700;">管理后台</h2>
        <div style="display:flex; gap:8px; align-items:center">
          <span class="text-sm text-muted">{{ adminUser?.nickname || '管理员' }}</span>
          <button class="btn btn-ghost btn-sm" @click="handleLogout">退出</button>
          <router-link to="/" class="btn btn-ghost btn-sm">返回首页</router-link>
        </div>
      </div>
    </header>

    <div class="container" style="padding-top: var(--spacing-xl); padding-bottom: var(--spacing-xl);">
      <!-- Tab 切换 -->
      <div class="admin-tabs">
        <button class="admin-tab" :class="{ active: tab === 'stats' }" @click="tab = 'stats'">数据统计</button>
        <button class="admin-tab" :class="{ active: tab === 'review' }" @click="tab = 'review'">
          食谱审核
          <span v-if="pendingTotal > 0" class="tab-badge">{{ pendingTotal }}</span>
        </button>
        <button class="admin-tab" :class="{ active: tab === 'users' }" @click="switchTab('users')">用户管理</button>
      </div>

      <!-- Tab: 数据统计 -->
      <div v-if="tab === 'stats'">
        <div class="stats-row">
          <div class="card stat-card">
            <span class="stat-value">{{ stats.users }}</span>
            <span class="stat-label">注册用户</span>
          </div>
          <div class="card stat-card">
            <span class="stat-value">{{ stats.foods }}</span>
            <span class="stat-label">食物条目</span>
          </div>
          <div class="card stat-card">
            <span class="stat-value">{{ stats.recipes }}</span>
            <span class="stat-label">已审核食谱</span>
          </div>
        </div>
      </div>

      <!-- Tab: 食谱审核 -->
      <div v-if="tab === 'review'">
        <!-- 加载中 -->
        <div v-if="reviewLoading" class="text-center" style="padding: 60px 0;">
          <p class="text-muted">加载待审核食谱...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="pendingRecipes.length === 0" class="text-center" style="padding: 60px 0;">
          <span style="font-size:48px; display:block; margin-bottom:12px">✅</span>
          <p class="text-muted">暂无待审核食谱</p>
        </div>

        <!-- 待审核列表 -->
        <div v-else class="review-list">
          <div v-for="r in pendingRecipes" :key="r.id" class="card review-card">
            <div class="review-header">
              <div class="review-info">
                <h3>{{ r.name }}</h3>
                <div class="review-meta">
                  <span>👤 {{ r.author }}</span>
                  <span v-if="r.cuisine" class="tag tag-default">{{ r.cuisine }}</span>
                  <span v-if="r.calories" class="text-xs text-muted">{{ r.calories }}千卡/100g</span>
                  <span class="text-xs text-muted">{{ formatDate(r.created_at) }}</span>
                </div>
                <p v-if="r.description" class="review-desc text-sm">{{ r.description }}</p>
              </div>
              <div class="review-actions">
                <button
                  class="btn btn-primary btn-sm"
                  :disabled="r._processing"
                  @click="handleApprove(r)"
                >
                  {{ r._processing ? '处理中...' : '✅ 通过' }}
                </button>
                <button
                  class="btn btn-outline btn-sm"
                  :disabled="r._processing"
                  @click="handleReject(r)"
                >
                  {{ r._processing ? '处理中...' : '❌ 拒绝' }}
                </button>
              </div>
            </div>
            <!-- 步骤展开 -->
            <details v-if="r.cooking_steps?.length" class="review-steps">
              <summary>查看烹饪步骤（{{ r.cooking_steps.length }}步）</summary>
              <ol>
                <li v-for="(s, i) in r.cooking_steps" :key="i">{{ s }}</li>
              </ol>
            </details>
          </div>
        </div>
      </div>

      <!-- Tab: 用户管理 -->
      <div v-if="tab === 'users'">
        <!-- 加载中 -->
        <div v-if="usersLoading" class="text-center" style="padding: 60px 0;">
          <p class="text-muted">加载用户列表...</p>
        </div>

        <!-- 用户表格 -->
        <div v-else class="card" style="overflow-x:auto">
          <table class="user-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>昵称</th>
                <th>邮箱</th>
                <th>身份</th>
                <th>状态</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in userList" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ u.nickname }}</td>
                <td>{{ u.email }}</td>
                <td>
                  <span v-if="u.is_admin" class="tag tag-danger">管理员</span>
                  <span v-else class="tag tag-default">普通用户</span>
                </td>
                <td>
                  <span v-if="u.is_active" class="tag tag-success">正常</span>
                  <span v-else class="tag tag-warning">已封禁</span>
                </td>
                <td class="text-sm text-muted">{{ formatDate(u.created_at) }}</td>
                <td class="user-actions-cell">
                  <button
                    v-if="u.is_active"
                    class="btn btn-outline btn-xs"
                    :disabled="u._processing"
                    @click="handleBan(u)"
                  >封禁</button>
                  <button
                    v-else
                    class="btn btn-primary btn-xs"
                    :disabled="u._processing"
                    @click="handleUnban(u)"
                  >解封</button>
                  <button
                    v-if="!u.is_admin"
                    class="btn btn-outline btn-xs"
                    :disabled="u._processing"
                    @click="handlePromote(u)"
                  >设为管理员</button>
                  <button
                    v-else
                    class="btn btn-outline btn-xs"
                    :disabled="u._processing"
                    @click="handleDemote(u)"
                  >取消管理员</button>
                  <button
                    class="btn btn-ghost btn-xs btn-danger-text"
                    :disabled="u._processing"
                    @click="handleDeleteUser(u)"
                  >删除</button>
                </td>
              </tr>
            </tbody>
          </table>
          <p v-if="usersTotal > userList.length" class="text-sm text-muted" style="text-align:center; margin-top:12px">
            共 {{ usersTotal }} 个用户，已加载 {{ userList.length }} 个
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getPendingRecipes, approveRecipe, rejectRecipe, getStats, getUsers, updateUser, deleteUser } from '../api/admin'

const router = useRouter()
const tab = ref('review')
const reviewLoading = ref(true)
const pendingRecipes = ref([])
const pendingTotal = ref(0)
const adminUser = ref(null)

const stats = ref({ users: 0, foods: 0, recipes: 0 })

// 用户管理
const usersLoading = ref(false)
const userList = ref([])
const usersTotal = ref(0)

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString('zh-CN')
}

function handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  router.push('/admin/login')
}

async function fetchStats() {
  try {
    const res = await getStats()
    stats.value = { users: res.users, foods: res.foods, recipes: res.recipes }
  } catch (e) {
    console.error('加载统计数据失败:', e)
  }
}

async function fetchPending() {
  reviewLoading.value = true
  try {
    const res = await getPendingRecipes()
    pendingRecipes.value = res.items || []
    pendingTotal.value = res.total || 0
  } catch (e) {
    console.error('加载审核列表失败:', e)
  } finally {
    reviewLoading.value = false
  }
}

async function handleApprove(r) {
  r._processing = true
  try {
    await approveRecipe(r.id)
    pendingRecipes.value = pendingRecipes.value.filter(item => item.id !== r.id)
    pendingTotal.value--
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    r._processing = false
  }
}

async function handleReject(r) {
  r._processing = true
  try {
    await rejectRecipe(r.id)
    pendingRecipes.value = pendingRecipes.value.filter(item => item.id !== r.id)
    pendingTotal.value--
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    r._processing = false
  }
}

// ===== 用户管理 =====
async function fetchUsers() {
  usersLoading.value = true
  try {
    const res = await getUsers()
    userList.value = res.items || []
    usersTotal.value = res.total || 0
  } catch (e) {
    console.error('加载用户列表失败:', e)
  } finally {
    usersLoading.value = false
  }
}

async function handleBan(u) {
  u._processing = true
  try {
    await updateUser(u.id, { is_active: false })
    u.is_active = false
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    u._processing = false
  }
}

async function handleUnban(u) {
  u._processing = true
  try {
    await updateUser(u.id, { is_active: true })
    u.is_active = true
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    u._processing = false
  }
}

async function handlePromote(u) {
  u._processing = true
  try {
    await updateUser(u.id, { is_admin: true })
    u.is_admin = true
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    u._processing = false
  }
}

async function handleDemote(u) {
  u._processing = true
  try {
    await updateUser(u.id, { is_admin: false })
    u.is_admin = false
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    u._processing = false
  }
}

async function handleDeleteUser(u) {
  if (!confirm(`确定要删除用户 "${u.nickname}" (${u.email}) 吗？此操作不可恢复。`)) return
  u._processing = true
  try {
    await deleteUser(u.id)
    userList.value = userList.value.filter(item => item.id !== u.id)
    usersTotal.value--
  } catch (e) {
    alert('操作失败：' + (e?.message || '网络错误'))
  } finally {
    u._processing = false
  }
}

function switchTab(t) {
  tab.value = t
  if (t === 'users') fetchUsers()
  if (t === 'stats') fetchStats()
}

onMounted(() => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try { adminUser.value = JSON.parse(userStr) } catch {}
  }
  fetchPending()
  fetchStats()
})
</script>

<style scoped>
.admin-tabs {
  display: flex;
  gap: 0;
  margin-bottom: var(--spacing-lg);
  border-bottom: 2px solid var(--color-border);
}
.admin-tab {
  padding: 10px 20px;
  border: none;
  background: none;
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}
.admin-tab:hover { color: var(--color-primary); }
.admin-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}
.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  background: #e74c3c;
  color: #fff;
  border-radius: 9px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}
.stat-card {
  text-align: center;
  padding: var(--spacing-xl) var(--spacing-lg);
}
.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: 800;
  color: var(--color-primary-dark);
  display: block;
}
.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.review-list { display: flex; flex-direction: column; gap: var(--spacing-md); }
.review-card { padding: var(--spacing-md); }
.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
}
.review-info { flex: 1; min-width: 0; }
.review-info h3 {
  font-size: var(--font-size-base);
  font-weight: 600;
  margin-bottom: 4px;
}
.review-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}
.review-desc {
  margin-top: 6px;
  color: var(--color-text);
  line-height: 1.5;
}
.review-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex-shrink: 0;
}
.review-steps {
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border);
}
.review-steps summary {
  font-size: var(--font-size-sm);
  color: var(--color-primary);
  cursor: pointer;
}
.review-steps ol {
  margin-top: 8px;
  padding-left: 20px;
  font-size: var(--font-size-sm);
  color: var(--color-text);
}
.review-steps li {
  margin-bottom: 4px;
  line-height: 1.5;
}

@media (max-width: 640px) {
  .stats-row { grid-template-columns: 1fr; }
  .review-header { flex-direction: column; }
  .review-actions { flex-direction: row; width: 100%; }
  .review-actions .btn { flex: 1; }
}

/* 用户表格 */
.user-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}
.user-table th,
.user-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}
.user-table th {
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg);
  white-space: nowrap;
}
.user-table tbody tr:hover {
  background: rgba(0,0,0,0.02);
}
.user-actions-cell {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.btn-xs {
  padding: 2px 8px;
  font-size: 12px;
}
.btn-danger-text {
  color: #e74c3c;
}
.btn-danger-text:hover {
  background: rgba(231, 76, 60, 0.08);
}
.tag-danger { background: rgba(231,76,60,0.1); color: #c0392b; }
.tag-success { background: rgba(46,204,113,0.1); color: #27ae60; }
.tag-warning { background: rgba(243,156,18,0.1); color: #d35400; }
</style>
