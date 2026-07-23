/** 美食广场 API */
import request from './request'

export function getRecipes(page = 1, pageSize = 12) {
  return request.get('/public/recipes', { params: { page, page_size: pageSize } })
}

export function getRecipeDetail(id) {
  return request.get(`/public/recipes/${id}`)
}

export function getComments(recipeId) {
  return request.get(`/public/recipes/${recipeId}/comments`)
}

export function addComment(recipeId, content) {
  return request.post(`/public/recipes/${recipeId}/comment`, { content })
}

export function saveRecipe(recipeId) {
  return request.post(`/public/recipes/${recipeId}/save`)
}

export function unsaveRecipe(recipeId) {
  return request.delete(`/public/recipes/${recipeId}/save`)
}
