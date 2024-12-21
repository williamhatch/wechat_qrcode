import axios from 'axios'
import { message } from 'ant-design-vue'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',  // 添加 /api 前缀，这样请求会被 Vite 代理
  withCredentials: false,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    message.error('请求发送失败')
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log('收到响应:', response.data)
    return response
  },
  error => {
    // 处理 511 错误
    if (error.response && error.response.status === 511) {
      // 在新窗口打开 localtunnel URL 让用户确认
      window.open(error.response.headers.location || api.defaults.baseURL, '_blank')
      message.warning('请在新窗口中确认访问权限，然后重试')
      return Promise.reject(new Error('请确认访问权限后重试'))
    }

    console.error('请求失败:', error)
    
    if (error.response) {
      // 服务器返回错误状态码
      switch (error.response.status) {
        case 403:
          message.error('没有权限访问')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error('服务器内部错误')
          break
        default:
          message.error('请求失败，请稍后重试')
      }
    } else if (error.request) {
      // 请求发送成功，但没有收到响应
      message.error('无法连接到服务器，请检查网络连接')
    } else {
      // 请求配置出错
      message.error('请求配置错误')
    }
    
    return Promise.reject(error)
  }
)

export default api
