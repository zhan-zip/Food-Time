import request from './request'

/** 注册 */
export function register(data) {
  return request.post('/auth/register', data)
}

/** 登录 */
export function login(data) {
  return request.post('/auth/login', data)
}

/** 发送验证码 */
export function sendCode(data) {
  return request.post('/auth/send-code', data)
}

/** 验证邮箱 */
export function verifyEmail(data) {
  return request.post('/auth/verify-email', data)
}

/** 获取当前用户 */
export function getMe() {
  return request.get('/auth/me')
}

/** 修改资料 */
export function updateProfile(data) {
  return request.put('/auth/profile', data)
}
