import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/scheduled-tasks',
    name: 'ScheduledTasks',
    component: () => import('../views/ScheduledTasks.vue')
  },
  {
    path: '/outbound',
    name: 'Outbound',
    component: () => import('../views/Outbound.vue')
  },
  {
    path: '/rules',
    name: 'Rules',
    component: () => import('../views/Rules.vue')
  },
  {
    path: '/inbound',
    name: 'Inbound',
    component: () => import('../views/Inbound.vue')
  },
  {
    path: '/dns',
    name: 'DNS',
    component: () => import('../views/DNS.vue')
  },
  {
    path: '/other-settings',
    name: 'OtherSettings',
    component: () => import('../views/OtherSettings.vue')
  },
  {
    path: '/config-files',
    name: 'ConfigFiles',
    component: () => import('../views/ConfigFiles.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 