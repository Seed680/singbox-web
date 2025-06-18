<template>
  <page-container>
    <div class="other-settings">
      <div class="page-header">
        <h2 class="page-title">其他设置</h2>
      </div>

      <!-- 实验性功能配置 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>实验性功能配置</span>
            <el-button 
              type="primary" 
              @click="handleSaveExperimental"
              :loading="loading.experimental">
              <el-icon><Check /></el-icon>
              {{ loading.experimental ? '保存中...' : '保存' }}
            </el-button>
          </div>
        </template>
        <div 
          id="experimentalEditor" 
          style="width: 100%; height: 400px;"
          v-loading="loading.experimental || configLoading">
        </div>
      </el-card>

      <!-- 日志配置 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>日志配置</span>
            <el-button 
              type="primary" 
              @click="handleSaveLog"
              :loading="loading.log">
              <el-icon><Check /></el-icon>
              {{ loading.log ? '保存中...' : '保存' }}
            </el-button>
          </div>
        </template>
        <div 
          id="logEditor" 
          style="width: 100%; height: 400px;"
          v-loading="loading.log || configLoading">
        </div>
      </el-card>
    </div>
  </page-container>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageContainer from '../components/PageContainer.vue'
import JSONEditor from 'jsoneditor'
import 'jsoneditor/dist/jsoneditor.css'

// API 基础路径
const API_BASE = '/api'

// 编辑器实例
const experimentalEditor = ref(null)
const logEditor = ref(null)

// 加载状态
const loading = reactive({
  experimental: false,
  log: false
})
const configLoading = ref(false)

// 初始化实验性功能编辑器
const initExperimentalEditor = () => {
  const container = document.getElementById('experimentalEditor')
  const options = {
    mode: 'code',
    modes: ['code', 'tree', 'view', 'form', 'text'],
    onError: function (err) {
      ElMessage.error('JSON 格式错误：' + err.toString())
    },
    mainMenuBar: true,
    navigationBar: false,
    statusBar: true,
    colorPicker: false,
    search: true,
    format: true,
    repair: true
  }
  experimentalEditor.value = new JSONEditor(container, options)
}

  // 初始化日志编辑器
const initLogEditor = () => {
  const container = document.getElementById('logEditor')
  const options = {
    mode: 'code',
    modes: ['code', 'tree', 'view', 'form', 'text'],
    onError: function (err) {
      ElMessage.error('JSON 格式错误：' + err.toString())
    },
    mainMenuBar: true,
    navigationBar: false,
    statusBar: true,
    colorPicker: false,
    search: true,
    format: true,
    repair: true
  }
  logEditor.value = new JSONEditor(container, options)
}

// 加载配置
const loadConfig = async () => {
  try {
    configLoading.value = true
    const response = await fetch(`${API_BASE}/config`)
    if (response.ok) {
    const data = await response.json()

      // 设置实验性功能配置
    if (experimentalEditor.value) {
      experimentalEditor.value.set(data.main.experimental || {})
    }
      
      // 设置日志配置
    if (logEditor.value) {
      logEditor.value.set(data.main.log || {})
      }
    } else {
      ElMessage.error('加载配置失败')
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败，请检查后端服务是否启动')
  } finally {
    configLoading.value = false
  }
}

// 保存实验性功能配置
const handleSaveExperimental = async () => {
  try {
    loading.experimental = true
    // 获取编辑器中的内容
    const experimentalConfig = experimentalEditor.value.get()
    
    const response = await fetch(`${API_BASE}/experimental`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ experimental: experimentalConfig })
    })
    
    if (response.ok) {
      ElMessage.success('实验性功能配置保存成功')
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '实验性功能配置保存失败')
    }
  } catch (error) {
    console.error('保存实验性功能配置失败:', error)
    ElMessage.error('保存失败，请检查JSON格式是否正确')
  } finally {
    loading.experimental = false
  }
}

// 保存日志配置
const handleSaveLog = async () => {
  try {
    loading.log = true
    // 获取编辑器中的内容
    const logConfig = logEditor.value.get()
    
    const response = await fetch(`${API_BASE}/log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ log: logConfig })
    })
    
    if (response.ok) {
      ElMessage.success('日志配置保存成功')
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '日志配置保存失败')
    }
  } catch (error) {
    console.error('保存日志配置失败:', error)
    ElMessage.error('保存失败，请检查JSON格式是否正确')
  } finally {
    loading.log = false
  }
}

// 页面加载时初始化
onMounted(() => {
  initExperimentalEditor()
  initLogEditor()
  // 延迟一下再加载数据，确保编辑器已经完全初始化
  setTimeout(() => {
    loadConfig()
  }, 100)
})

// 页面卸载时清理
onBeforeUnmount(() => {
  if (experimentalEditor.value) {
    experimentalEditor.value.destroy()
  }
  if (logEditor.value) {
    logEditor.value.destroy()
  }
})
</script>

<style scoped>
.other-settings {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 500;
  color: #303133;
}

.box-card {
  margin-bottom: 20px;
  transition: all 0.3s;
}

.box-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.jsoneditor) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

:deep(.jsoneditor-menu) {
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
}
</style> 