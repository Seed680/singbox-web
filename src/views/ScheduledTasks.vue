<template>
  <page-container>
    <div class="scheduled-tasks">
      <div class="page-header">
        <h2 class="page-title">定时任务</h2>
      </div>

      <!-- 订阅更新任务 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>订阅更新</span>
            <div class="header-actions">
              <el-button type="primary" @click="handleRunNow('subscription')" :loading="subscriptionRunning">
                <el-icon><VideoPlay /></el-icon>
                立即运行
              </el-button>
              <el-switch
                v-model="subscriptionTask.enabled"
                :active-value="true"
                :inactive-value="false"
                inline-prompt
                :active-text="'启用'"
                :inactive-text="'禁用'"
              />
            </div>
          </div>
        </template>
        <el-form :model="subscriptionTask" label-width="120px">
          <el-form-item label="执行周期">
            <el-select v-model="subscriptionTask.schedule.type" class="schedule-type">
              <el-option label="每小时" value="hourly" />
              <el-option label="每天" value="daily" />
              <el-option label="每周" value="weekly" />
              <el-option label="自定义" value="custom" />
            </el-select>

            <!-- 自定义 Cron 表达式 -->
            <el-input
              v-if="subscriptionTask.schedule.type === 'custom'"
              v-model="subscriptionTask.schedule.cron"
              placeholder="Cron 表达式 (例如: 0 0 * * *)"
              class="cron-input"
            />

            <!-- 每天执行时间 -->
            <el-time-picker
              v-if="subscriptionTask.schedule.type === 'daily'"
              v-model="subscriptionTask.schedule.time"
              format="HH:mm"
              placeholder="选择时间"
              class="time-picker"
            />

            <!-- 每周执行时间 -->
            <template v-if="subscriptionTask.schedule.type === 'weekly'">
              <el-select v-model="subscriptionTask.schedule.dayOfWeek" class="day-select">
                <el-option label="周一" value="1" />
                <el-option label="周二" value="2" />
                <el-option label="周三" value="3" />
                <el-option label="周四" value="4" />
                <el-option label="周五" value="5" />
                <el-option label="周六" value="6" />
                <el-option label="周日" value="0" />
              </el-select>
              <el-time-picker
                v-model="subscriptionTask.schedule.time"
                format="HH:mm"
                placeholder="选择时间"
                class="time-picker"
              />
            </template>

            <!-- 每小时的分钟数 -->
            <el-input-number
              v-if="subscriptionTask.schedule.type === 'hourly'"
              v-model="subscriptionTask.schedule.minute"
              :min="0"
              :max="59"
              placeholder="分钟"
              class="minute-input"
            />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Singbox 内核更新任务 -->
      <el-card class="box-card">
        <template #header>
          <div class="card-header">
            <span>Singbox 内核更新</span>
            <div class="header-actions">
              <el-button type="primary" @click="handleRunNow('singbox')" :loading="singboxRunning">
                <el-icon><VideoPlay /></el-icon>
                立即运行
              </el-button>
              <el-switch
                v-model="singboxTask.enabled"
                :active-value="true"
                :inactive-value="false"
                inline-prompt
                :active-text="'启用'"
                :inactive-text="'禁用'"
              />
            </div>
          </div>
        </template>
        <el-form :model="singboxTask" label-width="120px">
          <el-form-item label="执行周期">
            <el-select v-model="singboxTask.schedule.type" class="schedule-type">
              <el-option label="每小时" value="hourly" />
              <el-option label="每天" value="daily" />
              <el-option label="每周" value="weekly" />
              <el-option label="自定义" value="custom" />
            </el-select>

            <!-- 自定义 Cron 表达式 -->
            <el-input
              v-if="singboxTask.schedule.type === 'custom'"
              v-model="singboxTask.schedule.cron"
              placeholder="Cron 表达式 (例如: 0 0 * * *)"
              class="cron-input"
            />

            <!-- 每天执行时间 -->
            <el-time-picker
              v-if="singboxTask.schedule.type === 'daily'"
              v-model="singboxTask.schedule.time"
              format="HH:mm"
              placeholder="选择时间"
              class="time-picker"
            />

            <!-- 每周执行时间 -->
            <template v-if="singboxTask.schedule.type === 'weekly'">
              <el-select v-model="singboxTask.schedule.dayOfWeek" class="day-select">
                <el-option label="周一" value="1" />
                <el-option label="周二" value="2" />
                <el-option label="周三" value="3" />
                <el-option label="周四" value="4" />
                <el-option label="周五" value="5" />
                <el-option label="周六" value="6" />
                <el-option label="周日" value="0" />
              </el-select>
              <el-time-picker
                v-model="singboxTask.schedule.time"
                format="HH:mm"
                placeholder="选择时间"
                class="time-picker"
              />
            </template>

            <!-- 每小时的分钟数 -->
            <el-input-number
              v-if="singboxTask.schedule.type === 'hourly'"
              v-model="singboxTask.schedule.minute"
              :min="0"
              :max="59"
              placeholder="分钟"
              class="minute-input"
            />
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 保存按钮 -->
      <div class="actions">
        <el-button 
          type="primary" 
          @click="handleSave"
          :loading="loading">
          <el-icon><Check /></el-icon>
          {{ loading ? '保存中...' : '保存配置' }}
        </el-button>
      </div>
    </div>
  </page-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Check, VideoPlay } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PageContainer from '../components/PageContainer.vue'

// 加载状态
const loading = ref(false)
const configLoading = ref(false)

// 订阅更新任务
const subscriptionTask = ref({
  enabled: true,
  schedule: {
    type: 'daily',
    time: new Date(2000, 0, 1, 3, 0), // 默认凌晨 3 点
    dayOfWeek: '1',
    minute: 0,
    cron: '0 3 * * *'
  }
})

// Singbox 内核更新任务
const singboxTask = ref({
  enabled: true,
  schedule: {
    type: 'weekly',
    time: new Date(2000, 0, 1, 4, 0), // 默认凌晨 4 点
    dayOfWeek: '1',
    minute: 0,
    cron: '0 4 * * 1'
  }
})

// 任务运行状态
const subscriptionRunning = ref(false)
const singboxRunning = ref(false)

// 获取任务配置
const fetchTasks = async () => {
  try {
    configLoading.value = true
          const response = await fetch('/api/tasks')
    const data = await response.json()
    if (data.success) {
      // 转换时间字符串为 Date 对象
      if (data.tasks.subscription) {
        const subTask = data.tasks.subscription
        subscriptionTask.value = {
          ...subTask,
          schedule: {
            ...subTask.schedule,
            time: subTask.schedule.time ? new Date(`2000-01-01T${subTask.schedule.time}`) : null
          }
        }
      }
      if (data.tasks.singbox) {
        const sbTask = data.tasks.singbox
        singboxTask.value = {
          ...sbTask,
          schedule: {
            ...sbTask.schedule,
            time: sbTask.schedule.time ? new Date(`2000-01-01T${sbTask.schedule.time}`) : null
          }
        }
      }
    }
  } catch (error) {
    console.error('获取任务配置失败:', error)
    ElMessage.error('获取任务配置失败')
  } finally {
    configLoading.value = false
  }
}

// 保存任务配置
const handleSave = async () => {
  try {
    loading.value = true
    // 转换配置格式
    const tasks = {
      subscription: {
        ...subscriptionTask.value,
        schedule: {
          ...subscriptionTask.value.schedule,
          time: subscriptionTask.value.schedule.time 
            ? subscriptionTask.value.schedule.time.toTimeString().slice(0, 5) 
            : null
        }
      },
      singbox: {
        ...singboxTask.value,
        schedule: {
          ...singboxTask.value.schedule,
          time: singboxTask.value.schedule.time 
            ? singboxTask.value.schedule.time.toTimeString().slice(0, 5) 
            : null
        }
      }
    }

    const response = await fetch('/api/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(tasks)
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success('保存成功')
    } else {
      ElMessage.error(data.error || '保存失败')
    }
  } catch (error) {
    console.error('保存任务配置失败:', error)
    ElMessage.error('保存任务配置失败')
  } finally {
    loading.value = false
  }
}

// 立即运行任务
const handleRunNow = async (taskType) => {
  try {
    if (taskType === 'subscription' && subscriptionRunning.value) {
      return
    }
    if (taskType === 'singbox' && singboxRunning.value) {
      return
    }

    // 设置对应的运行状态
    if (taskType === 'subscription') {
      subscriptionRunning.value = true
    } else {
      singboxRunning.value = true
    }

    const response = await fetch(`/api/tasks/run/${taskType}`, {
      method: 'POST'
    })

    const data = await response.json()
    if (data.success) {
      ElMessage.success('任务执行成功')
    } else {
      ElMessage.error(data.error || '任务执行失败')
    }
  } catch (error) {
    console.error(`执行${taskType}任务失败:`, error)
    ElMessage.error(`执行任务失败: ${error.message}`)
  } finally {
    // 重置运行状态
    if (taskType === 'subscription') {
      subscriptionRunning.value = false
    } else {
      singboxRunning.value = false
    }
  }
}

onMounted(() => {
  fetchTasks()
})
</script>

<style scoped>
.scheduled-tasks {
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

.schedule-type {
  width: 120px;
  margin-right: 16px;
}

.cron-input {
  width: 200px;
}

.time-picker {
  width: 120px;
  margin-right: 16px;
}

.day-select {
  width: 100px;
  margin-right: 16px;
}

.minute-input {
  width: 120px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style> 