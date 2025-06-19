// 全局请求拦截器
const originalFetch = window.fetch

window.fetch = function(url, options = {}) {
  // 跳过登录和下载相关的API
  if (url.includes('/api/auth/login') || url.includes('/api/config/download/')) {
    return originalFetch(url, options)
  }
  
  // 获取token
  const token = localStorage.getItem('auth_token')
  
  // 如果有token，添加到请求头
  if (token && url.includes('/api/')) {
    options.headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  }
  
  return originalFetch(url, options).then(response => {
    // 如果返回401，说明token无效，跳转到登录页
    if (response.status === 401 && !url.includes('/api/auth/')) {
      localStorage.removeItem('auth_token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return response
  })
}

export default {
  // 导出一些工具函数
  getToken() {
    return localStorage.getItem('auth_token')
  },
  
  setToken(token) {
    localStorage.setItem('auth_token', token)
  },
  
  removeToken() {
    localStorage.removeItem('auth_token')
  },
  
  logout() {
    this.removeToken()
    window.location.href = '/login'
  }
} 