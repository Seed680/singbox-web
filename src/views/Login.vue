<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-pattern"></div>
    </div>
    
    <div class="login-content">
      <div class="login-wrapper">
        <div class="login-header">
          <div class="logo-section">
            <img src="/vite.svg" alt="Logo" class="login-logo" />
            <h1 class="app-title">SingBox Web</h1>
          </div>
          <p class="login-subtitle">管理系统</p>
        </div>
        
        <el-card class="login-card" shadow="hover">
          <div class="card-content">
            <h2 class="form-title">登录</h2>
            
            <el-form 
              :model="loginForm" 
              :rules="rules" 
              ref="loginFormRef"
              class="login-form"
              @submit.prevent="handleLogin">
              
              <el-form-item prop="username" class="form-item">
                <el-input 
                  v-model="loginForm.username" 
                  placeholder="请输入用户名"
                  size="large"
                  class="form-input"
                  @keyup.enter="handleLogin">
                  <template #prefix>
                    <el-icon class="input-icon"><User /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item prop="password" class="form-item">
                <el-input 
                  v-model="loginForm.password" 
                  type="password" 
                  placeholder="请输入密码"
                  size="large"
                  class="form-input"
                  show-password
                  @keyup.enter="handleLogin">
                  <template #prefix>
                    <el-icon class="input-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item class="form-item submit-item">
                <el-button 
                  type="primary" 
                  size="large"
                  :loading="loading"
                  @click="handleLogin"
                  class="login-button">
                  <span v-if="!loading">登录</span>
                  <span v-else>登录中...</span>
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: loginForm.username,
        password: loginForm.password
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      // 保存token到localStorage
      localStorage.setItem('auth_token', data.token)
      ElMessage.success('登录成功')
      
      // 跳转到仪表盘
      router.push('/')
    } else {
      ElMessage.error(data.error || '登录失败')
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error('登录失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 全屏容器 */
.login-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 背景 */
.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  z-index: 1;
}

.bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 内容区域 */
.login-content {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 380px;
  padding: 60px 24px 40px;
}

.login-wrapper {
  width: 100%;
}

/* 头部区域 */
.login-header {
  text-align: center;
  margin-bottom: 40px;
  color: white;
}

.logo-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.login-logo {
  width: 48px;
  height: 48px;
  filter: brightness(0) invert(1);
}

.app-title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.login-subtitle {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
  font-weight: 300;
}

/* 登录卡片 */
.login-card {
  border-radius: 16px;
  border: none;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.card-content {
  padding: 32px 28px;
}

.form-title {
  text-align: center;
  margin: 0 0 32px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

/* 表单样式 */
.login-form {
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
}

.form-item {
  margin-bottom: 24px;
}

.submit-item {
  margin-bottom: 0;
  margin-top: 32px;
}

.form-input {
  --el-input-border-radius: 12px;
}

.input-icon {
  color: #909399;
}

.login-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-content {
    max-width: 100%;
    padding: 40px 20px 30px;
  }
  
  .card-content {
    padding: 24px 20px;
  }
  
  .login-header {
    margin-bottom: 32px;
  }
  
  .app-title {
    font-size: 28px;
  }
  
  .form-title {
    font-size: 20px;
    margin-bottom: 24px;
  }
  
  .form-item {
    margin-bottom: 20px;
  }
  
  .submit-item {
    margin-top: 24px;
  }
}

@media (max-width: 480px) {
  .login-content {
    padding: 30px 16px 20px;
  }
  
  .card-content {
    padding: 20px 16px;
  }
  
  .login-form {
    max-width: 280px;
  }
  
  .login-header {
    margin-bottom: 24px;
  }
  
  .logo-section {
    gap: 8px;
  }
  
  .login-logo {
    width: 40px;
    height: 40px;
  }
  
  .app-title {
    font-size: 24px;
  }
  
  .login-subtitle {
    font-size: 14px;
  }
  
  .form-title {
    font-size: 18px;
    margin-bottom: 20px;
  }
  
  .login-button {
    height: 44px;
    font-size: 15px;
  }
}

@media (max-height: 600px) {
  .login-header {
    margin-bottom: 20px;
  }
  
  .card-content {
    padding: 20px 24px;
  }
  
  .form-title {
    margin-bottom: 20px;
  }
  
  .form-item {
    margin-bottom: 16px;
  }
  
  .submit-item {
    margin-top: 20px;
  }
}

/* 深色模式兼容 */
@media (prefers-color-scheme: dark) {
  .login-card {
    background: rgba(30, 30, 30, 0.95);
  }
  
  .form-title {
    color: #e5eaf3;
  }
}

/* 高对比度支持 */
@media (prefers-contrast: high) {
  .login-background {
    background: #000;
  }
  
  .login-card {
    background: #fff;
    border: 2px solid #000;
  }
}

/* 去除表单项的深层样式覆盖 */
:deep(.el-form-item__label) {
  display: none;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px var(--el-color-primary) inset;
}

:deep(.el-card__body) {
  padding: 0;
}
</style> 