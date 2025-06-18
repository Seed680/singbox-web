<template>
  <page-container>
    <div class="outbound">
      <div class="page-header">
        <h2 class="page-title">出站配置</h2>
      </div>

      <!-- 订阅部分 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>订阅</span>
            <el-button type="primary" @click="handleAddSubscription" :loading="loading.subscription">
              <el-icon><Plus /></el-icon>
              添加订阅
            </el-button>
          </div>
        </template>
        <el-table :data="subscriptions" style="width: 100%" v-loading="loading.config">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="url" label="链接" show-overflow-tooltip />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button-group>
                <el-button 
                  type="primary" 
                  @click="handleEditSubscription(row)"
                  :loading="loading.subscription"
                  :disabled="loading.subscription">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button 
                  type="danger" 
                  @click="handleDeleteSubscription(row)"
                  :loading="loading.delete"
                  :disabled="loading.delete">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 过滤器部分 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>过滤器</span>
            <el-button type="primary" @click="handleAddFilter" :loading="loading.filter">
              <el-icon><Plus /></el-icon>
              添加过滤器
            </el-button>
          </div>
        </template>
        <el-table :data="filters" style="width: 100%" v-loading="loading.config">
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="include" label="包含关键字" show-overflow-tooltip />
          <el-table-column prop="exclude" label="排除关键字" show-overflow-tooltip />
          <el-table-column prop="mode" label="模式">
            <template #default="{ row }">
              <el-tag :type="row.mode === 'select' ? 'success' : 'warning'">
                {{ row.mode === 'select' ? '节点选择' : '速度测试' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button-group>
                <el-button 
                  type="primary" 
                  @click="handleEditFilter(row)"
                  :loading="loading.filter"
                  :disabled="loading.filter">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button 
                  type="danger" 
                  @click="handleDeleteFilter(row)"
                  :loading="loading.delete"
                  :disabled="loading.delete">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 额外出站部分 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>额外出站</span>
            <el-button 
              type="primary" 
              @click="handleSaveExtraOutbounds"
              :loading="loading.extraOutbounds">
              <el-icon><Check /></el-icon>
              {{ loading.extraOutbounds ? '保存中...' : '保存' }}
            </el-button>
          </div>
        </template>
        <div 
          id="extraOutboundsEditor" 
          style="width: 100%; height: 400px;"
          v-loading="loading.config">
        </div>
      </el-card>

      <!-- 订阅对话框 -->
      <el-dialog
        v-model="subscriptionDialog.visible"
        :title="subscriptionDialog.isEdit ? '编辑订阅' : '添加订阅'"
        width="500px"
        :close-on-click-modal="false">
        <el-form :model="subscriptionDialog.form" label-width="100px">
          <el-form-item label="名称" required>
            <el-input 
              v-model="subscriptionDialog.form.name" 
              placeholder="请输入订阅名称"
              :disabled="loading.subscription" />
          </el-form-item>
          <el-form-item label="URL" required>
            <el-input 
              v-model="subscriptionDialog.form.url" 
              placeholder="请输入订阅地址"
              :disabled="loading.subscription" />
            <div class="form-item-tip">请填写singbox格式的订阅链接，推荐使用substore进行订阅转换</div>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="subscriptionDialog.visible = false" :disabled="loading.subscription">
            取消
          </el-button>
          <el-button 
            type="primary" 
            @click="handleSaveSubscription"
            :loading="loading.subscription">
            {{ loading.subscription ? '保存中...' : '确定' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- 过滤器对话框 -->
      <el-dialog
        v-model="filterDialog.visible"
        :title="filterDialog.isEdit ? '编辑过滤器' : '添加过滤器'"
        width="500px"
        :close-on-click-modal="false">
        <el-form :model="filterDialog.form" label-width="100px">
          <el-form-item label="名称" required>
            <el-input v-model="filterDialog.form.name" :disabled="loading.filter" />
          </el-form-item>
          <el-form-item label="包含关键字">
            <el-input v-model="filterDialog.form.include" :disabled="loading.filter" />
          </el-form-item>
          <el-form-item label="排除关键字">
            <el-input v-model="filterDialog.form.exclude" :disabled="loading.filter" />
          </el-form-item>
          <el-form-item label="全部节点">
            <el-switch v-model="filterDialog.form.allNodes" :disabled="loading.filter" />
          </el-form-item>
          <el-form-item label="节点" v-if="!filterDialog.form.allNodes">
            <el-select 
              v-model="filterDialog.form.node" 
              placeholder="请选择节点"
              :disabled="loading.filter">
              <el-option
                v-for="item in nodeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="模式" required>
            <el-select v-model="filterDialog.form.mode" :disabled="loading.filter">
              <el-option label="节点选择" value="select" />
              <el-option label="速度测试" value="urltest" />
            </el-select>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="filterDialog.visible = false" :disabled="loading.filter">
              取消
            </el-button>
            <el-button 
              type="primary" 
              @click="handleSaveFilter"
              :loading="loading.filter">
              {{ loading.filter ? '保存中...' : '确定' }}
            </el-button>
          </span>
        </template>
      </el-dialog>
    </div>
  </page-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { Plus, Edit, Delete, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageContainer from '../components/PageContainer.vue'
import { globalConfig } from '../globalConfig'
import JSONEditor from 'jsoneditor'
import 'jsoneditor/dist/jsoneditor.css'

// API 基础路径
const API_BASE = '/api'

// 额外出站编辑器
const extraOutboundsEditor = ref(null)

// 加载状态
const loading = reactive({
  config: false,
  subscription: false,
  filter: false,
  extraOutbounds: false,
  delete: false
})

// 补充模板依赖的变量和空方法，保证页面正常渲染
const subscriptions = ref([])
const filters = ref([])
const subscriptionDialog = reactive({
  visible: false,
  isEdit: false,
  form: {
    name: '',
    url: '',
    lastUpdate: ''
  }
})
const filterDialog = reactive({ 
  visible: false, 
  isEdit: false, 
  form: { name: '', include: '', exclude: '', allNodes: true, node: '', mode: 'select' } 
})
const nodeOptions = computed(() => {
  // 根据订阅列表生成节点选项
  return subscriptions.value.map(sub => ({
    label: sub.name,
    value: sub.name
  }))
})

// 初始化额外出站编辑器
const initExtraOutboundsEditor = () => {
  const container = document.getElementById('extraOutboundsEditor')
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
  extraOutboundsEditor.value = new JSONEditor(container, options)
}

// 加载配置
const loadConfig = async () => {
  try {
    loading.config = true
    const response = await fetch(`${API_BASE}/config`)
    if (response.ok) {
      const data = await response.json()
      // 从 subscribe 字段获取订阅相关配置
      subscriptions.value = data.subscribe.subscriptions || []
      filters.value = data.subscribe.filters || []
      // 设置额外出站配置
      if (extraOutboundsEditor.value) {
        const exOutbounds = data.subscribe.ex_outbounds || []
        extraOutboundsEditor.value.set(exOutbounds)
      }
    } else {
      ElMessage.error('加载配置失败')
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败，请检查后端服务是否启动')
  } finally {
    loading.config = false
  }
}

// 添加订阅
const handleAddSubscription = () => {
  subscriptionDialog.visible = true
  subscriptionDialog.isEdit = false
  subscriptionDialog.form = { 
    name: '', 
    url: '', 
    lastUpdate: '' 
  }
}

// 编辑订阅
const handleEditSubscription = (subscription) => {
  subscriptionDialog.visible = true
  subscriptionDialog.isEdit = true
  subscriptionDialog.form = { 
    name: subscription.name,
    url: subscription.url,
    lastUpdate: subscription.lastUpdate
  }
}

// 删除订阅
const handleDeleteSubscription = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该订阅吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    loading.delete = true
    const response = await fetch(`${API_BASE}/subscription/${encodeURIComponent(row.name)}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('删除成功')
      await loadConfig() // 重新加载配置
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除订阅失败:', error)
      ElMessage.error('删除失败')
    }
  } finally {
    loading.delete = false
  }
}

// 保存订阅
const handleSaveSubscription = async () => {
  if (!subscriptionDialog.form.name || !subscriptionDialog.form.url) {
    ElMessage.warning('请填写名称和URL')
    return
  }
  
  try {
    loading.subscription = true
    const response = await fetch(`${API_BASE}/subscription`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: subscriptionDialog.form.name,
        url: subscriptionDialog.form.url,
        lastUpdate: subscriptionDialog.form.lastUpdate
      })
    })
    
    if (response.ok) {
      ElMessage.success(subscriptionDialog.isEdit ? '编辑成功' : '添加成功')
      subscriptionDialog.visible = false
      await loadConfig() // 重新加载配置
    } else {
      const data = await response.json()
      ElMessage.error(data.error || '保存失败')
    }
  } catch (error) {
    console.error('保存订阅失败:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.subscription = false
  }
}

// 过滤器相关方法
const handleAddFilter = () => {
  filterDialog.visible = true
  filterDialog.isEdit = false
  filterDialog.form = { 
    name: '', 
    include: '', 
    exclude: '', 
    allNodes: true, 
    node: '', 
    mode: 'select' 
  }
}

const handleEditFilter = (row) => {
  filterDialog.visible = true
  filterDialog.isEdit = true
  filterDialog.form = { ...row }
}

const handleDeleteFilter = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该过滤器吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    loading.delete = true
    const response = await fetch(`${API_BASE}/filter/${encodeURIComponent(row.name)}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      ElMessage.success('删除成功')
      await loadConfig() // 重新加载配置
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除过滤器失败:', error)
      ElMessage.error('删除失败')
    }
  } finally {
    loading.delete = false
  }
}

// 保存过滤器
const handleSaveFilter = async () => {
  if (!filterDialog.form.name || !filterDialog.form.mode) {
    ElMessage.warning('请填写名称和模式')
    return
  }
  
  // 如果没有选择全部节点，但也没有选择具体节点，提示错误
  if (!filterDialog.form.allNodes && !filterDialog.form.node) {
    ElMessage.warning('请选择节点')
    return
  }
  
  try {
    loading.filter = true
    console.log('正在保存过滤器:', filterDialog.form)
    const response = await fetch(`${API_BASE}/filter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(filterDialog.form)
    })
    
    const responseData = await response.json()
    
    if (response.ok) {
      ElMessage.success(filterDialog.isEdit ? '编辑成功' : '添加成功')
      filterDialog.visible = false
      await loadConfig() // 重新加载配置
    } else {
      console.error('保存过滤器失败:', responseData)
      ElMessage.error(responseData.error || '保存失败')
    }
  } catch (error) {
    console.error('保存过滤器异常:', error)
    ElMessage.error(`保存失败: ${error.message}`)
  } finally {
    loading.filter = false
  }
}

// 保存额外出站
const handleSaveExtraOutbounds = async () => {
  try {
    loading.extraOutbounds = true
    // 获取编辑器中的内容
    const exOutbounds = extraOutboundsEditor.value.get()
    
    // 验证是否为数组
    if (!Array.isArray(exOutbounds)) {
      ElMessage.error('额外出站必须是一个 JSON 数组')
      return
    }
    
    const response = await fetch(`${API_BASE}/extra-outbounds`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(exOutbounds)
    })
    
    if (response.ok) {
      ElMessage.success('额外出站配置保存成功')
      await loadConfig() // 重新加载配置
    } else {
      const error = await response.json()
      ElMessage.error(error.error || '保存失败')
    }
  } catch (error) {
    console.error('保存额外出站配置失败:', error)
    ElMessage.error('保存失败，请检查后端服务是否启动')
  } finally {
    loading.extraOutbounds = false
  }
}

// 页面加载时初始化
onMounted(() => {
  initExtraOutboundsEditor()
  // 延迟一下再加载数据，确保编辑器已经完全初始化
  setTimeout(() => {
    loadConfig()
  }, 100)
})

// 页面卸载时清理
onBeforeUnmount(() => {
  if (extraOutboundsEditor.value) {
    extraOutboundsEditor.value.destroy()
  }
})
</script>

<style scoped>
.outbound {
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

.form-item-tip {
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
  margin-top: 4px;
}

/* 额外出站输入框样式 */
.el-textarea__inner {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
  font-size: 14px;
  line-height: 1.6;
  tab-size: 2;
}

/* 卡片头部按钮组样式 */
.card-header > div {
  display: flex;
  gap: 10px;
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