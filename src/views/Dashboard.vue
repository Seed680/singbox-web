<template>
  <page-container>
    <div class="dashboard">
      <h2 class="page-title">仪表盘</h2>
      <p class="page-description">管理和监控您的 Sing-box 代理服务状态</p>
      <el-card class="status-card">
            <template #header>
              <div class="card-header">
            <span>Sing-box 服务状态</span>
              </div>
            </template>
        <div class="status-content">
          <div class="status-info">
            <el-tag :type="serviceStatus ? 'success' : 'danger'" class="status-tag">
              {{ serviceStatus ? '运行中' : '已停止' }}
            </el-tag>
            </div>
          <div class="status-actions">
            <el-button 
              type="primary" 
              :loading="actionLoading"
              @click="handleStart" 
              :disabled="serviceStatus">
              立即运行
            </el-button>
            <el-button 
              type="danger" 
              :loading="actionLoading"
              @click="handleStop" 
              :disabled="!serviceStatus">
              停止服务
            </el-button>
              </div>
            </div>
          </el-card>
    </div>
  </page-container>
</template>

<script setup>
import PageContainer from '../components/PageContainer.vue'
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'

const serviceStatus = ref(false)
const actionLoading = ref(false)
let statusInterval = null

// 获取服务状态
const getStatus = async () => {
  try {
    const response = await fetch('/api/singbox/status')
    const data = await response.json()
    if (data.success) {
      serviceStatus.value = data.running
    }
  } catch (error) {
    console.error('获取服务状态失败:', error)
  }
}

// 启动服务
const handleStart = async () => {
  if (actionLoading.value) return
  actionLoading.value = true
  try {
    const response = await fetch('/api/singbox/start', {
      method: 'POST'
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('服务启动成功')
      await getStatus()
    } else {
      ElMessage.error(data.error || '服务启动失败')
    }
  } catch (error) {
    console.error('启动服务失败:', error)
    ElMessage.error('启动服务失败')
  } finally {
    actionLoading.value = false
  }
}

// 停止服务
const handleStop = async () => {
  if (actionLoading.value) return
  actionLoading.value = true
  try {
    const response = await fetch('/api/singbox/stop', {
      method: 'POST'
    })
    const data = await response.json()
    if (data.success) {
      ElMessage.success('服务停止成功')
      await getStatus()
    } else {
      ElMessage.error(data.error || '服务停止失败')
    }
  } catch (error) {
    console.error('停止服务失败:', error)
    ElMessage.error('停止服务失败')
  } finally {
    actionLoading.value = false
  }
}

// 组件挂载时开始定时获取状态
onMounted(() => {
  getStatus()
  statusInterval = setInterval(getStatus, 5000) // 每5秒更新一次状态
})

// 组件卸载时清除定时器
onBeforeUnmount(() => {
  if (statusInterval) {
    clearInterval(statusInterval)
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.page-title {
  margin-bottom: 8px;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
  text-align: center;
}

.page-description {
  margin-bottom: 30px;
  font-size: 14px;
  color: #606266;
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-card {
  max-width: 600px;
  margin: 40px auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: center;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.status-tag {
  font-size: 16px;
  padding: 8px 16px;
}

.status-actions {
  display: flex;
  gap: 16px;
}
</style> 