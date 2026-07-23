import request from './request'

/** 查询账单记录 */
export function getExpenseRecords(params = {}) {
  return request.get('/expense/records', { params })
}

/** 新增账单 */
export function createExpenseRecord(data) {
  return request.post('/expense/records', data)
}

/** 删除账单 */
export function deleteExpenseRecord(recordId) {
  return request.delete(`/expense/records/${recordId}`)
}

/** 账单统计 */
export function getExpenseStats(period = 'month') {
  return request.get('/expense/stats', { params: { period } })
}

/** OCR 识图记账 */
export function ocrExpense(imageBase64) {
  return request.post('/expense/ocr', { image_base64: imageBase64 })
}
