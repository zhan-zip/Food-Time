import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器：自动附加 Token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    // 提取可读错误信息（detail 可能是字符串、数组或对象）
    let msg = '请求失败'
    const detail = error.response?.data?.detail
    if (detail) {
      if (Array.isArray(detail)) {
        msg = detail.map(i => i.msg || JSON.stringify(i)).join('; ')
      } else if (typeof detail === 'object') {
        msg = detail.msg || detail.message || JSON.stringify(detail)
      } else {
        msg = String(detail)
      }
    } else {
      msg = error.message || '请求失败'
    }
    return Promise.reject(new Error(msg))
  }
)

export default request
