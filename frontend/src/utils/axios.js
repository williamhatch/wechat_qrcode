import axios from 'axios'
import { message } from 'ant-design-vue'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:5001',
  withCredentials: true,  // 允许跨域请求携带凭证
  timeout: 10000,  // 设置超时时间
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 添加请求拦截器
api.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    console.log('发送请求:', config.url)
    return config
  },
  error => {
    console.error('请求错误:', error)
    message.error('请求发送失败')
    return Promise.reject(error)
  }
)

// 添加响应拦截器
api.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    console.log('收到响应:', response.data)
    return response
  },
  error => {
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
