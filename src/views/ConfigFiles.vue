<template>
  <PageContainer title="配置文件管理">
    <div class="config-files-container">
      <!-- 左侧 base_config.json -->
      <div class="config-panel">
        <div class="panel-header">
          <h3>基础配置 (base_config.json)</h3>
          <div class="panel-actions">
            <el-button 
              type="primary" 
              size="small" 
              :loading="baseConfigLoading"
              @click="saveBaseConfig"
              :disabled="baseConfigLoading"
            >
              {{ baseConfigLoading ? '保存中...' : '保存基础配置' }}
            </el-button>
            <el-button 
              size="small" 
              @click="loadBaseConfig"
              :disabled="baseConfigLoading"
            >
              重新加载
            </el-button>
          </div>
        </div>
        <div class="editor-container">
          <div 
            ref="baseConfigEditor" 
            class="json-editor"
            v-loading="baseConfigLoading"
            element-loading-text="加载中..."
          ></div>
        </div>
      </div>

      <!-- 右侧 config.json -->
      <div class="config-panel">
        <div class="panel-header">
          <h3>当前配置 (config.json)</h3>
          <div class="panel-actions">
            <el-button 
              type="primary" 
              size="small" 
              :loading="mainConfigLoading"
              @click="saveMainConfig"
              :disabled="mainConfigLoading"
            >
              {{ mainConfigLoading ? '保存中...' : '保存当前配置' }}
            </el-button>
            <el-button 
              size="small" 
              @click="loadMainConfig"
              :disabled="mainConfigLoading"
            >
              重新加载
            </el-button>
            <el-button 
              size="small" 
              type="warning"
              @click="resetToBaseConfig"
              :disabled="baseConfigLoading || mainConfigLoading"
            >
              重置为基础配置
            </el-button>
          </div>
        </div>
        <div class="editor-container">
          <div 
            ref="mainConfigEditor" 
            class="json-editor"
            v-loading="mainConfigLoading"
            element-loading-text="加载中..."
          ></div>
        </div>
      </div>
    </div>
  </PageContainer>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import JSONEditor from 'jsoneditor'
import 'jsoneditor/dist/jsoneditor.css'
import PageContainer from '../components/PageContainer.vue'

export default {
  name: 'ConfigFiles',
  components: {
    PageContainer
  },
  setup() {
    const baseConfigEditor = ref(null)
    const mainConfigEditor = ref(null)
    const baseConfigLoading = ref(false)
    const mainConfigLoading = ref(false)
    
    let baseEditor = null
    let mainEditor = null

    // 编辑器配置
    const editorOptions = {
      mode: 'code',
      themes: ['ace/theme/monokai'],
      language: 'json',
      indentation: 2,
      tabSize: 2,
      search: true,
      statusBar: true,
      navigationBar: true,
      onError: (error) => {
        console.error('JSON Editor Error:', error)
        ElMessage.error('JSON 格式错误: ' + error.message)
      }
    }

    // 加载基础配置
    const loadBaseConfig = async () => {
      baseConfigLoading.value = true
      try {
        const response = await fetch('/api/base-config')
        const data = await response.json()
        
        if (data.success) {
          if (baseEditor) {
            baseEditor.set(data.config)
            ElMessage.success('基础配置加载成功')
          } else {
            ElMessage.error('编辑器未初始化')
          }
        } else {
          throw new Error(data.error || '加载基础配置失败')
        }
      } catch (error) {
        console.error('加载基础配置失败:', error)
        ElMessage.error('加载基础配置失败: ' + error.message)
      } finally {
        baseConfigLoading.value = false
      }
    }

    // 保存基础配置
    const saveBaseConfig = async () => {
      if (!baseEditor) return
      
      try {
        const config = baseEditor.get()
        baseConfigLoading.value = true
        
        const response = await fetch('/api/base-config', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ config })
        })
        
        const data = await response.json()
        
        if (data.success) {
          ElMessage.success('基础配置保存成功')
        } else {
          throw new Error(data.error || '保存基础配置失败')
        }
      } catch (error) {
        console.error('保存基础配置失败:', error)
        ElMessage.error('保存基础配置失败: ' + error.message)
      } finally {
        baseConfigLoading.value = false
      }
    }

    // 加载当前配置
    const loadMainConfig = async () => {
      mainConfigLoading.value = true
      try {
        const response = await fetch('/api/config')
        const data = await response.json()
        
        if (data.success) {
          if (mainEditor) {
            mainEditor.set(data.config)
            ElMessage.success('当前配置加载成功')
          } else {
            ElMessage.error('编辑器未初始化')
          }
        } else {
          throw new Error(data.error || '加载当前配置失败')
        }
      } catch (error) {
        console.error('加载当前配置失败:', error)
        ElMessage.error('加载当前配置失败: ' + error.message)
      } finally {
        mainConfigLoading.value = false
      }
    }

    // 保存当前配置
    const saveMainConfig = async () => {
      if (!mainEditor) return
      
      try {
        const config = mainEditor.get()
        mainConfigLoading.value = true
        
        const response = await fetch('/api/config', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(config)
        })
        
        const data = await response.json()
        
        if (data.success) {
          ElMessage.success('当前配置保存成功')
        } else {
          throw new Error(data.error || '保存当前配置失败')
        }
      } catch (error) {
        console.error('保存当前配置失败:', error)
        ElMessage.error('保存当前配置失败: ' + error.message)
      } finally {
        mainConfigLoading.value = false
      }
    }

    // 重置为基础配置
    const resetToBaseConfig = async () => {
      try {
        await ElMessageBox.confirm(
          '确定要将当前配置重置为基础配置吗？这将立即覆盖 config.json 文件。',
          '重置确认',
          {
            confirmButtonText: '确定重置',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        // 调用新的后端API来执行重置
        const response = await fetch('/api/config/reset', { method: 'POST' })
        const data = await response.json()
        
        if (response.ok && data.success) {
          ElMessage.success('当前配置已成功重置！正在重新加载...')
          // 重置成功后，重新加载右侧的编辑器
          await loadMainConfig()
        } else {
          throw new Error(data.error || '重置失败')
        }
      } catch (error) {
        // 如果用户点击了"取消"，则不显示错误消息
        if (error !== 'cancel' && error.message !== 'cancel') {
          console.error('重置配置失败:', error)
          ElMessage.error('重置失败: ' + (error.message || error))
        }
      }
    }

    // 初始化编辑器
    const initEditors = () => {
      try {
        if (baseConfigEditor.value && !baseEditor) {
          baseEditor = new JSONEditor(baseConfigEditor.value, {
            ...editorOptions,
            onChange: () => {
              // 可以在这里添加实时验证逻辑
            }
          })
        }
        
        if (mainConfigEditor.value && !mainEditor) {
          mainEditor = new JSONEditor(mainConfigEditor.value, {
            ...editorOptions,
            onChange: () => {
              // 可以在这里添加实时验证逻辑
            }
          })
        }
      } catch (error) {
        console.error('编辑器初始化失败:', error)
        ElMessage.error('编辑器初始化失败: ' + error.message)
      }
    }

    // 销毁编辑器
    const destroyEditors = () => {
      if (baseEditor) {
        baseEditor.destroy()
        baseEditor = null
      }
      if (mainEditor) {
        mainEditor.destroy()
        mainEditor = null
      }
    }

    onMounted(async () => {
      // 等待DOM渲染完成
      await new Promise(resolve => setTimeout(resolve, 100))
      
      try {
        initEditors()
        
        // 确保编辑器已初始化
        await new Promise(resolve => setTimeout(resolve, 200))
        
        // 加载配置
        await Promise.all([
          loadBaseConfig(),
          loadMainConfig()
        ])
      } catch (error) {
        console.error('初始化过程出错:', error)
        ElMessage.error('页面初始化失败: ' + error.message)
      }
    })

    onUnmounted(() => {
      destroyEditors()
    })

    return {
      baseConfigEditor,
      mainConfigEditor,
      baseConfigLoading,
      mainConfigLoading,
      loadBaseConfig,
      saveBaseConfig,
      loadMainConfig,
      saveMainConfig,
      resetToBaseConfig
    }
  }
}
</script>

<style scoped>
.config-files-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 200px);
  min-height: 600px;
}

.config-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.editor-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.json-editor {
  height: 100%;
  width: 100%;
}

/* JSONEditor 样式覆盖 */
:deep(.jsoneditor) {
  border: none;
  height: 100% !important;
}

:deep(.jsoneditor-menu) {
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.ace-jsoneditor) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
}

:deep(.jsoneditor-statusbar) {
  background: #f5f7fa;
  border-top: 1px solid #e4e7ed;
  color: #606266;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .config-files-container {
    flex-direction: column;
    height: auto;
  }
  
  .config-panel {
    min-height: 400px;
  }
}

/* 加载状态样式 */
.el-loading-mask {
  background-color: rgba(255, 255, 255, 0.8);
}
</style> 