import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../utils/axios'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const qrCodeUrl = ref('')
  const scene = ref('')
  const checkingInterval = ref(null)

  const getQRCode = async () => {
    try {
      const response = await api.get('/wechat/get_qr_code')
      qrCodeUrl.value = response.data.qr_code_url
      scene.value = response.data.scene
      startPolling()
    } catch (error) {
      console.error('Failed to get QR code:', error)
    }
  }

  const checkLoginStatus = async () => {
    try {
      const response = await api.post('/wechat/check_login', {
        scene: scene.value
      })
      
      if (response.data.is_logged_in) {
        isLoggedIn.value = true
        stopPolling()
      }
    } catch (error) {
      console.error('Failed to check login status:', error)
    }
  }

  const startPolling = () => {
    if (!checkingInterval.value) {
      checkingInterval.value = setInterval(checkLoginStatus, 2000)
    }
  }

  const stopPolling = () => {
    if (checkingInterval.value) {
      clearInterval(checkingInterval.value)
      checkingInterval.value = null
    }
  }

  const logout = () => {
    isLoggedIn.value = false
    qrCodeUrl.value = ''
    scene.value = ''
    stopPolling()
  }

  return {
    isLoggedIn,
    qrCodeUrl,
    scene,
    getQRCode,
    logout
  }
})
