<template>
  <div class="page-container">
    <transition name="fade-transform" mode="out-in">
      <div class="page-content">
        <slot></slot>
      </div>
    </transition>
  </div>
</template>

<script setup>
// 无需额外的逻辑
</script>

<style scoped>
.page-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
  min-height: calc(100vh - 120px);
}

.page-content {
  animation: fadeIn 0.3s ease-in-out;
}

/* 淡入淡出 + 位移效果 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style> 