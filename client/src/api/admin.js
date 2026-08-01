import request from './request'

/** 获取待审核食谱列表 */
export function getPendingRecipes(page = 1, pageSize = 20) {
  return request.get('/admin/recipes/pending', { params: { page, page_size: pageSize } })
}

/** 审核通过食谱 */
export function approveRecipe(id) {
  return request.post(`/admin/recipes/${id}/approve`)
}

/** 拒绝食谱 */
export function rejectRecipe(id) {
  return request.post(`/admin/recipes/${id}/reject`)
}

/** 获取统计数据 */
export function getStats() {
  return request.get('/admin/stats')
}

/** 获取用户列表 */
export function getUsers(page = 1, pageSize = 20) {
  return request.get('/admin/users', { params: { page, page_size: pageSize } })
}

/** 更新用户（封禁/解封、设置/取消管理员） */
export function updateUser(userId, data) {
  return request.put(`/admin/users/${userId}`, data)
}

/** 删除用户 */
export function deleteUser(userId) {
  return request.delete(`/admin/users/${userId}`)
}

/** 获取已删除用户审计记录 */
export function getDeletedUsers(page = 1, pageSize = 20) {
  return request.get('/admin/deleted-users', { params: { page, page_size: pageSize } })
}
