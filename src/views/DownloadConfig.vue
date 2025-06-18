<template>
  <div class="download-config">
    <PageContainer>
      <el-card>
        <template #header>
          <div class="card-header">
            <span>下载配置</span>
          </div>
        </template>
        <div class="download-form">
          <el-form :model="form" label-width="120px">
            <el-form-item label="下载密码">
              <el-input v-model="form.password" placeholder="请设置下载配置文件的密码"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="savePassword" :loading="loading.save">保存密码</el-button>
              <el-button type="success" @click="downloadConfig" :loading="loading.download">下载配置</el-button>
            </el-form-item>
            <el-form-item label="下载链接" v-if="form.password">
              <div class="download-url">
                <el-input
                  v-model="downloadUrl"
                  readonly
                  :disabled="!form.password"
                >
                  <template #append>
                    <el-button @click="copyUrl">复制</el-button>
                  </template>
                </el-input>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </PageContainer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import PageContainer from '../components/PageContainer.vue'
import { ElMessage } from 'element-plus'

const form = ref({
  password: ''
})

const loading = ref({
  save: false,
  download: false
})

// 计算下载URL
const downloadUrl = computed(() => {
  if (!form.value.password) return ''
  const baseUrl = window.location.origin
  return `${baseUrl}/api/config/download/${encodeURIComponent(form.value.password)}`
})

// 复制下载链接
const copyUrl = async () => {
  try {
    await navigator.clipboard.writeText(downloadUrl.value)
    ElMessage.success('下载链接已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 获取已保存的密码
const getPassword = async () => {
  try {
    const response = await fetch('/api/config/download-password')
    if (response.ok) {
      const data = await response.json()
      form.value.password = data.password || ''
    }
  } catch (error) {
    console.error('获取密码失败:', error)
  }
}

const savePassword = async () => {
  if (!form.value.password) {
    ElMessage.warning('请输入下载密码')
    return
  }
  
  loading.value.save = true
  try {
    const response = await fetch('/api/config/download-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        password: form.value.password
      })
    })
    
    if (response.ok) {
      ElMessage.success('密码设置成功')
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '密码设置失败')
    }
  } catch (error) {
    console.error('设置密码失败:', error)
    ElMessage.error('网络错误')
  } finally {
    loading.value.save = false
  }
}

const downloadConfig = async () => {
  if (!form.value.password) {
    ElMessage.warning('请先设置并保存下载密码')
    return
  }
  
  loading.value.download = true
  try {
    // 先验证密码是否正确
    const response = await fetch(`/api/config/download/${encodeURIComponent(form.value.password)}`)
    if (response.ok) {
      // 如果密码正确，直接下载文件
      window.location.href = downloadUrl.value
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '下载失败')
    }
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('网络错误')
  } finally {
    loading.value.download = false
  }
}

// 页面加载时获取已保存的密码
onMounted(() => {
  getPassword()
})
</script>

<style scoped>
.download-form {
  max-width: 500px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.download-url {
  width: 100%;
}

.download-url :deep(.el-input-group__append) {
  padding: 0;
}

.download-url :deep(.el-input-group__append button) {
  border: none;
  margin: 0;
  height: 100%;
}
</style> 