/** 美食广场 API */
import request from './request'

export function getRecipes(page = 1, pageSize = 12, extraParams = {}) {
  return request.get('/public/recipes', { params: { page, page_size: pageSize, ...extraParams } })
}

export function getRecipeDetail(id) {
  return request.get(`/public/recipes/${id}`)
}

export function getComments(recipeId) {
  return request.get(`/public/recipes/${recipeId}/comments`)
}

export function addComment(recipeId, content, parentId) {
  return request.post(`/public/recipes/${recipeId}/comment`, { content, parent_id: parentId || null })
}

export function deleteComment(recipeId, commentId) {
  return request.delete(`/public/recipes/${recipeId}/comments/${commentId}`)
}

export function getCommentSummary(recipeId) {
  return request.get(`/public/recipes/${recipeId}/comment-summary`)
}

export function saveRecipe(recipeId) {
  return request.post(`/public/recipes/${recipeId}/save`)
}

export function getFavorites() {
  return request.get('/public/favorites')
}

export function getFavoriteRecipes() {
  return request.get('/public/favorites/recipes')
}

export function unsaveRecipe(recipeId) {
  return request.delete(`/public/recipes/${recipeId}/save`)
}
