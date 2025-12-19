<template>
  <div :class="statusClasses" class="status-indicator">
    <div v-if="status === 'saving'" class="loading-spinner"></div>
    <div v-else class="status-dot"></div>
    <span class="status-text">{{ statusText }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  status: 'saved' | 'saving' | 'error'
}

const props = defineProps<Props>()

const statusClasses = computed(() => ({
  'status-saved': props.status === 'saved',
  'status-saving': props.status === 'saving',
  'status-error': props.status === 'error'
}))

const statusText = computed(() => {
  switch (props.status) {
    case 'saved':
      return '已保存'
    case 'saving':
      return '保存中...'
    case 'error':
      return '保存失败'
    default:
      return ''
  }
})
</script>

<style scoped>
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.status-saved {
  background-color: #d5f4e6;
  color: #27ae60;
}

.status-saving {
  background-color: #fef9e7;
  color: #f39c12;
}

.status-error {
  background-color: #fadbd8;
  color: #e74c3c;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-saved .status-dot {
  background-color: #27ae60;
}

.status-error .status-dot {
  background-color: #e74c3c;
}

.loading-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #f39c12;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .status-indicator {
    padding: 0.2rem 0.4rem;
    font-size: 11px;
  }
  
  .status-dot {
    width: 6px;
    height: 6px;
  }
  
  .loading-spinner {
    width: 10px;
    height: 10px;
    border-width: 1.5px;
  }
}

@media (max-width: 480px) {
  .status-indicator {
    padding: 0.15rem 0.3rem;
    font-size: 10px;
  }
  
  .status-text {
    display: none;
  }
  
  .status-dot {
    width: 6px;
    height: 6px;
  }
  
  .loading-spinner {
    width: 8px;
    height: 8px;
  }
}
</style>