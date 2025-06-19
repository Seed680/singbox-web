import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

// 检查认证状态
const checkAuth = async () => {
  const token = localStorage.getItem('auth_token')
  if (!token) return false
  
  try {
    const response = await fetch('/api/auth/check', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const data = await response.json()
    return data.authenticated
  } catch (error) {
    console.error('认证检查失败:', error)
    return false
  }
}

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/scheduled-tasks',
    name: 'ScheduledTasks',
    component: () => import('../views/ScheduledTasks.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/outbound',
    name: 'Outbound',
    component: () => import('../views/Outbound.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('../views/Rules.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/inbound',
    name: 'Inbound',
    component: () => import('../views/Inbound.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/dns',
    name: 'DNS',
    component: () => import('../views/DNS.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/other-settings',
    name: 'OtherSettings',
    component: () => import('../views/OtherSettings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/config-files',
    name: 'ConfigFiles',
    component: () => import('../views/ConfigFiles.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/download-config',
    name: 'DownloadConfig',
    component: () => import('../views/DownloadConfig.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/change-password',
    name: 'ChangePassword',
    component: () => import('../views/ChangePassword.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局导航守卫
router.beforeEach(async (to, from, next) => {
  // 如果是登录页面，直接放行
  if (to.path === '/login') {
    next()
    return
  }
  
  // 检查是否需要认证
  if (to.meta.requiresAuth !== false) {
    const isAuthenticated = await checkAuth()
    if (!isAuthenticated) {
      ElMessage.warning('请先登录')
      next('/login')
      return
    }
  }
  
  next()
})

export default router 