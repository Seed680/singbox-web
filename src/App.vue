<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Monitor, Setting, Expand, Fold, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const activeMenu = computed(() => {
  const pathToMenuMap = {
    '/dashboard': '1-1',
    '/scheduled-tasks': '1-2',
    '/outbound': '2-1',
    '/rules': '2-2',
    '/inbound': '2-3',
    '/dns': '2-4',
    '/other-settings': '2-5',
    '/config-files': '2-6',
    '/download-config': '2-7'
  }
  return pathToMenuMap[route.path] || '1-1'
})
const isCollapse = ref(false)

const currentRoute = computed(() => {
  const routeMap = {
    '/dashboard': '仪表盘',
    '/scheduled-tasks': '定时任务',
    '/outbound': '出站',
    '/rules': '规则',
    '/inbound': '入站',
    '/dns': 'DNS',
    '/other-settings': '其他设置',
    '/config-files': '配置文件',
    '/download-config': '下载配置'
  }
  return routeMap[route.path] || '首页'
})

const handleSelect = (key) => {
  const routeMap = {
    '1-1': '/dashboard',
    '1-2': '/scheduled-tasks',
    '2-1': '/outbound',
    '2-2': '/rules',
    '2-3': '/inbound',
    '2-4': '/dns',
    '2-5': '/other-settings',
    '2-6': '/config-files',
    '2-7': '/download-config'
  }
  router.push(routeMap[key])
}

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleRefresh = () => {
  router.go(0)
}
</script>

<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '200px'" class="aside">
      <div class="logo-container">
        <img src="/vite.svg" alt="Logo" class="logo" :class="{ 'logo-collapse': isCollapse }" />
        <span class="title" v-show="!isCollapse">SingBox</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical"
        @select="handleSelect"
        :collapse="isCollapse"
        :collapse-transition="false"
      >
        <el-sub-menu index="1">
          <template #title>
            <el-icon><Monitor /></el-icon>
            <span>监控</span>
          </template>
          <el-menu-item index="1-1">仪表盘</el-menu-item>
          <el-menu-item index="1-2">定时任务</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="2">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>配置</span>
          </template>
          <el-menu-item index="2-1">出站</el-menu-item>
          <el-menu-item index="2-2">规则</el-menu-item>
          <el-menu-item index="2-3">入站</el-menu-item>
          <el-menu-item index="2-4">DNS</el-menu-item>
          <el-menu-item index="2-5">其他设置</el-menu-item>
          <el-menu-item index="2-6">配置文件</el-menu-item>
          <el-menu-item index="2-7">下载配置</el-menu-item>
        </el-sub-menu>
      </el-menu>
      <div class="collapse-btn" @click="toggleCollapse">
        <el-icon :class="{ 'is-collapse': isCollapse }">
          <component :is="isCollapse ? 'Expand' : 'Fold'" />
        </el-icon>
      </div>
    </el-aside>
    <el-container class="main-container" :class="{ 'collapse': isCollapse }">
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRoute }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button type="primary" plain size="small" @click="handleRefresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </el-header>
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}

.layout-container {
  height: 100vh;
  width: 100vw;
  position: fixed;
  top: 0;
  left: 0;
}

.aside {
  background-color: #304156;
  color: #fff;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  overflow-y: auto;
  transition: width 0.3s;
  z-index: 1000;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  overflow: hidden;
  transition: all 0.3s;
  justify-content: flex-start;
}

.aside[style*="64px"] .logo-container {
  justify-content: center;
  padding: 0 16px;
}

.logo {
  width: 32px;
  height: 32px;
  transition: all 0.3s;
}

.logo-collapse {
  margin-left: 0;
}

.title {
  margin-left: 12px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  transition: all 0.3s;
}

.el-menu {
  border-right: none;
}

.el-menu-vertical {
  height: calc(100% - 120px);
}

.el-menu-vertical:not(.el-menu--collapse) {
  width: 200px;
}

.collapse-btn {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background-color: #263445;
}

.collapse-btn .el-icon {
  font-size: 20px;
  transition: transform 0.3s;
}

.collapse-btn .is-collapse {
  transform: rotate(180deg);
}

.main-container {
  margin-left: 200px;
  transition: margin-left 0.3s;
}

.main-container.collapse {
  margin-left: 64px;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left, .header-right {
  display: flex;
  align-items: center;
}

.el-main {
  padding: 20px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 60px);
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
  .aside {
    transform: translateX(-100%);
}
  
  .aside.show {
    transform: translateX(0);
  }
  
  .main-container {
    margin-left: 0;
  }
  
  .header {
    padding: 0 10px;
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 滚动条样式 */
.aside::-webkit-scrollbar {
  width: 6px;
}

.aside::-webkit-scrollbar-thumb {
  background-color: #4a5064;
  border-radius: 3px;
}

.aside::-webkit-scrollbar-track {
  background-color: #304156;
}
</style>
