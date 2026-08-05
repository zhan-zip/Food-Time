import request from './request'

/** 查询饮食记录 */
export function getDietRecords(params = {}) {
  return request.get('/diet/records', { params })
}

/** 新增饮食记录 */
export function createDietRecord(data) {
  return request.post('/diet/records', data)
}

/** 删除饮食记录 */
export function deleteDietRecord(recordId) {
  return request.delete(`/diet/records/${recordId}`)
}

/** 获取偏好分析 */
export function getPreferences() {
  return request.get('/diet/preferences')
}

/** 获取营养分析 */
export function getNutrition(days = 7) {
  return request.get('/diet/nutrition', { params: { days } })
}

/** 获取营养对照《膳食指南》评估（实际 vs 推荐 vs 状态） */
export function getNutritionAssessment(days = 7) {
  return request.get('/diet/nutrition-assessment', { params: { days } })
}
