<template>
  <page-container>
    <div class="dns">
      <div class="page-header">
        <h2 class="page-title">DNS 配置</h2>
        <el-button 
          type="primary" 
          @click="handleSaveDNS"
          :loading="loading">
          <el-icon><Check /></el-icon>
          {{ loading ? '保存中...' : '保存' }}
        </el-button>
      </div>

      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>DNS 配置</span>
          </div>
        </template>
        <div 
          id="dnsEditor" 
          style="width: 100%; height: 500px;"
          v-loading="loading || configLoading">
        </div>
      </el-card>
    </div>
  </page-container>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageContainer from '../components/PageContainer.vue'
import JSONEditor from 'jsoneditor'
import 'jsoneditor/dist/jsoneditor.css'

// API 基础路径
const API_BASE = '/api'

// DNS编辑器
const dnsEditor = ref(null)

// 加载状态
const loading = ref(false)
const configLoading = ref(false)

// 初始化DNS编辑器
const initDNSEditor = () => {
  const container = document.getElementById('dnsEditor')
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
  dnsEditor.value = new JSONEditor(container, options)
}

// 加载DNS配置
const loadDNSConfig = async () => {
  try {
    configLoading.value = true
    const response = await fetch(`${API_BASE}/dns`)
    if (response.ok) {
    const data = await response.json()
      if (dnsEditor.value) {
        dnsEditor.value.set(data.dns || {})
      }
    } else {
      ElMessage.error('加载DNS配置失败')
    }
  } catch (error) {
    console.error('加载DNS配置失败:', error)
    ElMessage.error('加载DNS配置失败，请检查后端服务是否启动')
  } finally {
    configLoading.value = false
  }
}

// 保存DNS配置
const handleSaveDNS = async () => {
  try {
    loading.value = true
    // 获取编辑器中的内容
    const dnsConfig = dnsEditor.value.get()
    
    const response = await fetch(`${API_BASE}/dns`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ dns: dnsConfig })
    })
    
    if (response.ok) {
      ElMessage.success('DNS配置保存成功')
    } else {
      const error = await response.json()
      ElMessage.error(error.error || 'DNS配置保存失败')
    }
  } catch (error) {
    console.error('保存DNS配置失败:', error)
    ElMessage.error('保存失败，请检查JSON格式是否正确')
  } finally {
    loading.value = false
  }
}

// 页面加载时初始化
onMounted(() => {
  initDNSEditor()
  // 延迟一下再加载数据，确保编辑器已经完全初始化
  setTimeout(() => {
    loadDNSConfig()
  }, 100)
})

// 页面卸载时清理
onBeforeUnmount(() => {
  if (dnsEditor.value) {
    dnsEditor.value.destroy()
  }
})
</script>

<style scoped>
.dns {
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