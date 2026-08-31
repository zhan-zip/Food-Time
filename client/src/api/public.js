/** 美食广场 API */
import request from './request'

/** 广场食谱分页列表（extraParams 追加筛选参数） */
export function getRecipes(page = 1, pageSize = 12, extraParams = {}) {
  return request.get('/public/recipes', { params: { page, page_size: pageSize, ...extraParams } })
}

/** 食谱详情 */
export function getRecipeDetail(id) {
  return request.get(`/public/recipes/${id}`)
}

/** 获取食谱评论列表 */
export function getComments(recipeId) {
  return request.get(`/public/recipes/${recipeId}/comments`)
}

/** 发表评论（parentId 存在时为回复某条评论） */
export function addComment(recipeId, content, parentId) {
  return request.post(`/public/recipes/${recipeId}/comment`, { content, parent_id: parentId || null })
}

/** 删除评论 */
export function deleteComment(recipeId, commentId) {
  return request.delete(`/public/recipes/${recipeId}/comments/${commentId}`)
}

/** 获取评论摘要 */
export function getCommentSummary(recipeId) {
  return request.get(`/public/recipes/${recipeId}/comment-summary`)
}

/** 收藏食谱 */
export function saveRecipe(recipeId) {
  return request.post(`/public/recipes/${recipeId}/save`)
}

/** 获取我的收藏列表 */
export function getFavorites() {
  return request.get('/public/favorites')
}

/** 获取收藏的食谱 */
export function getFavoriteRecipes() {
  return request.get('/public/favorites/recipes')
}

/** 取消收藏食谱 */
export function unsaveRecipe(recipeId) {
  return request.delete(`/public/recipes/${recipeId}/save`)
}
