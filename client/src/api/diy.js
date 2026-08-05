import request from './request'

/** 获取 DIY 食材列表（按冰箱分区） */
export function getDIYIngredients() {
  return request.get('/foods/ingredients')
}

/** AI 烹饪建议（forceAi=true 时库匹配 + AI 建议都返回，食材识别场景用） */
export function suggestRecipe({ ingredients, seasonings, forceAi = false }) {
  return request.post('/custom/suggest', { ingredients, seasonings, force_ai: forceAi })
}

/** 识别图片中的食材（Qwen VL 多模态） */
export function recognizeIngredients(imageBase64) {
  return request.post('/custom/recognize-ingredients', { image: imageBase64 })
}

/** 保存 DIY 食谱 */
export function saveRecipe(data) {
  return request.post('/custom/save', data)
}

/** 我的 DIY 食谱列表 */
export function getMyRecipes() {
  return request.get('/custom/my')
}

/** 将已保存食谱发布到广场 */
export function publishRecipe(recipeId) {
  return request.put(`/custom/${recipeId}/publish`)
}
