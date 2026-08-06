import request from './request'

/** 注册 */
export function register(data) {
  return request.post('/auth/register', data)
}

/** 登录 */
export function login(email, password) {
  return request.post('/auth/login', { email, password })
}

/** 发送验证码 */
export function sendCode(email) {
  return request.post('/auth/send-code', { email })
}

/** 验证邮箱 */
export function verifyEmail(email, code) {
  return request.post('/auth/verify-email', { email, code })
}

/** 忘记密码：发送重置验证码 */
export function forgotPassword(email) {
  return request.post('/auth/forgot-password', { email })
}

/** 忘记密码：验证码 + 新密码重置 */
export function resetPassword(data) {
  return request.post('/auth/reset-password', data)
}

/** 修改密码（登录状态：旧密码 + 新密码） */
export function changePassword(data) {
  return request.put('/auth/change-password', data)
}

/** 获取当前用户 */
export function getMe() {
  return request.get('/auth/me')
}

/** 修改资料 */
export function updateProfile(data) {
  return request.put('/auth/profile', data)
}
