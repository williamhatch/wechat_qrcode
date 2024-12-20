<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { message } from 'ant-design-vue'

const auth = useAuthStore()

onMounted(() => {
  if (!auth.isLoggedIn) {
    auth.getQRCode()
  }
})
</script>

<template>
  <div class="container">
    <div v-if="!auth.isLoggedIn" class="login-container">
      <h2>WeChat Login</h2>
      <div class="qr-code">
        <a-spin v-if="!auth.qrCodeUrl" />
        <img v-else :src="auth.qrCodeUrl" alt="WeChat QR Code" />
      </div>
      <p>Please scan the QR code with WeChat to login</p>
    </div>
    <div v-else class="welcome-container">
      <h1>成功登录!</h1>
      <a-button type="primary" @click="auth.logout">Logout</a-button>
    </div>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.qr-code {
  margin: 2rem 0;
  width: 200px;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.qr-code img {
  max-width: 100%;
  max-height: 100%;
}

.welcome-container {
  text-align: center;
  font-size: 1.5rem;
}

.welcome-container button {
  margin-top: 1rem;
}
</style>
