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
              <el-icon><CaretRight /></el-icon>
              立即运行
            </el-button>
            <el-button 
              type="danger" 
              :loading="actionLoading"
              @click="handleStop" 
              :disabled="!serviceStatus">
              <el-icon><VideoPause /></el-icon>
              停止服务
            </el-button>
            <el-button 
              type="warning" 
              :loading="actionLoading"
              @click="handleRestart" 
              :disabled="!serviceStatus">
              <el-icon><Refresh /></el-icon>
              重启服务
            </el-button>
            <el-button
              type="success"
              @click="handleOpenPanel"
              :disabled="!serviceStatus">
              <el-icon><View /></el-icon>
              打开面板
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
import { CaretRight, VideoPause, View, Refresh } from '@element-plus/icons-vue'

const serviceStatus = ref(false)
const actionLoading = ref(false)
let statusInterval = null

// 获取服务状态
const getStatus = async () => {
  try {
    const response = await fetch('/api/singbox/status')
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    serviceStatus.value = data.status === 'running'
  } catch (error) {
    console.error('获取服务状态失败:', error)
    // 出现错误时，保守地将状态设置为停止
    serviceStatus.value = false
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
    if (response.ok) {
      ElMessage.success(data.message || '服务启动成功')
      // 立即更新状态，而不是等待轮询
      serviceStatus.value = data.status === 'running'
    } else {
      ElMessage.error(data.message || '服务启动失败')
      serviceStatus.value = false
    }
  } catch (error) {
    console.error('启动服务失败:', error)
    ElMessage.error('启动服务失败，请检查后端日志')
    serviceStatus.value = false
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
    if (response.ok) {
      ElMessage.success(data.message || '服务停止成功')
      // 立即更新状态
      serviceStatus.value = data.status === 'running'
    } else {
      ElMessage.error(data.message || '服务停止失败')
    }
  } catch (error) {
    console.error('停止服务失败:', error)
    ElMessage.error('停止服务失败，请检查后端日志')
  } finally {
    actionLoading.value = false
  }
}

// 重启服务
const handleRestart = async () => {
  if (actionLoading.value) return
  actionLoading.value = true
  try {
    const response = await fetch('/api/singbox/restart', {
      method: 'POST'
    })
    const data = await response.json()
    if (response.ok) {
      ElMessage.success(data.message || '服务重启成功')
      // 立即更新状态
      serviceStatus.value = data.status === 'running'
    } else {
      ElMessage.error(data.message || '服务重启失败')
      serviceStatus.value = false
    }
  } catch (error) {
    console.error('重启服务失败:', error)
    ElMessage.error('重启服务失败，请检查后端日志')
    serviceStatus.value = false
  } finally {
    actionLoading.value = false
  }
}

// 打开 Clash API 面板
const handleOpenPanel = () => {
  const currentIp = window.location.hostname
  const url = `http://${currentIp}:9090/ui/`
  window.open(url, '_blank')
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