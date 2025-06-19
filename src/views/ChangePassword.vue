<template>
  <div class="change-password">
    <PageContainer>
      <el-card>
        <template #header>
          <div class="card-header">
            <span>修改密码</span>
          </div>
        </template>
        <div class="password-form">
          <el-form 
            :model="form" 
            :rules="rules" 
            ref="formRef"
            label-width="120px">
            <el-form-item label="当前密码" prop="oldPassword">
              <el-input 
                v-model="form.oldPassword" 
                type="password" 
                placeholder="请输入当前密码"
                show-password>
              </el-input>
            </el-form-item>
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="form.newPassword" 
                type="password" 
                placeholder="请输入新密码"
                show-password>
              </el-input>
            </el-form-item>
            <el-form-item label="确认新密码" prop="confirmPassword">
              <el-input 
                v-model="form.confirmPassword" 
                type="password" 
                placeholder="请再次输入新密码"
                show-password>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSubmit" :loading="loading">
                修改密码
              </el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
      </el-card>
    </PageContainer>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import PageContainer from '../components/PageContainer.vue'
import { ElMessage } from 'element-plus'

const formRef = ref()
const loading = ref(false)

const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入新密码'))
  } else if (value !== form.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  oldPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    loading.value = true
    
    const response = await fetch('/api/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        oldPassword: form.oldPassword,
        newPassword: form.newPassword
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      ElMessage.success('密码修改成功')
      resetForm()
    } else {
      ElMessage.error(data.error || '密码修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error('修改密码失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.password-form {
  max-width: 500px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 