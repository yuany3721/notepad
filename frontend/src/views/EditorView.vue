<template>
  <div class="editor-view">
    <div class="editor-header">
      <div class="editor-title">
        <h2>{{ displayName }}</h2>
        <div class="editor-actions">
          <button 
            @click="startRename" 
            class="btn btn-secondary btn-sm"
            title="重命名文件"
          >
            重命名
          </button>
          <button 
            @click="deleteFile" 
            class="btn btn-danger btn-sm"
            title="删除文件"
            :disabled="deletingFile"
          >
            {{ deletingFile ? '删除中...' : '删除' }}
          </button>
        </div>
      </div>
      <StatusIndicator :status="editorStore.saveStatus" />
    </div>
    <div class="editor-content">
      <textarea
        ref="editorElement"
        v-model="editorStore.content"
        @input="handleInput"
        :disabled="editorStore.isLoading"
        class="editor-textarea"
        placeholder="开始输入..."
      />
    </div>
    
    <!-- 调试工具（仅在测试模式下显示） -->
    <div v-if="testingMode" class="debug-tools">
      <button @click="testSave" class="btn btn-info btn-sm">测试保存</button>
      <button @click="toggleTestingMode" class="btn btn-secondary btn-sm">关闭调试</button>
      <div class="debug-info">
        <p>当前文件: {{ editorStore.currentFile }}</p>
        <p>保存状态: {{ editorStore.saveStatus }}</p>
        <p>内容长度: {{ editorStore.content.length }}</p>
      </div>
    </div>
    
    <!-- 重命名对话框 -->
    <div v-if="renamingFile" class="modal-overlay" @click="cancelRename">
      <div class="modal-content" @click.stop>
        <h3>重命名文件</h3>
        <form @submit.prevent="confirmRename">
          <div class="form-group">
            <label for="newFilename">新文件名</label>
            <input
              id="newFilename"
              v-model="newFilename"
              type="text"
              placeholder="请输入新文件名"
              class="form-input"
              ref="renameInput"
              maxlength="20"
              required
            />
            <small class="form-help">文件名最多20个字符，不能包含特殊字符</small>
          </div>
          <div class="modal-actions">
            <button
              type="button"
              @click="cancelRename"
              class="btn btn-secondary"
            >
              取消
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="!newFilename.trim()"
            >
              确认
            </button>
          </div>
        </form>
        <p v-if="renameError" class="error-message">{{ renameError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useEditorStore } from '@/stores/editor'
import { notesApi, filesApi } from '@/services/api'
import { useWebSocket } from '@/services/websocket'
import { emitter } from '@/utils/eventBus'
import StatusIndicator from '@/components/common/StatusIndicator.vue'

const route = useRoute()
const router = useRouter()
const editorStore = useEditorStore()
const { connect, sendSave, disconnect, getWebSocket } = useWebSocket()
const editorElement = ref<HTMLTextAreaElement>()
const renamingFile = ref(false)
const newFilename = ref('')
const renameError = ref('')
const renameInput = ref<HTMLInputElement>()
const deletingFile = ref(false)
const testingMode = ref(false) // 隐藏调试模式

// 计算属性，用于显示不含 .txt 后缀的文件名
const displayName = computed(() => {
  const filename = editorStore.currentFile
  if (filename.toLowerCase().endsWith('.txt')) {
    return filename.slice(0, -4)
  }
  return filename
})

const getDisplayName = (filename: string) => {
  if (filename.toLowerCase().endsWith('.txt')) {
    return filename.slice(0, -4)
  }
  return filename
}

let saveTimeout: number | null = null

const handleInput = () => {
  if (saveTimeout) {
    clearTimeout(saveTimeout)
  }
  
  editorStore.setSaveStatus('saving')
  saveTimeout = window.setTimeout(async () => {
    if (testingMode.value) {
      console.log('=== Auto Save Triggered ===')
      console.log('Attempting to save file:', editorStore.currentFile)
      console.log('Content length:', editorStore.content.length)
    }
    
    // 检查 WebSocket 连接状态
    const ws = getWebSocket()
    if (testingMode.value) {
      console.log('WebSocket instance:', ws)
      console.log('WebSocket readyState:', ws?.readyState)
      console.log('WebSocket OPEN constant:', WebSocket.OPEN)
    }
    
    if (ws && ws.readyState === WebSocket.OPEN) {
      if (testingMode.value) console.log('✅ Using WebSocket to save')
      try {
        if (testingMode.value) console.log('Sending to WebSocket with filename:', editorStore.currentFile)
        sendSave(editorStore.currentFile, editorStore.content)
        if (testingMode.value) console.log('WebSocket message sent, waiting for response...')
        // 设置超时，如果 WebSocket 5秒内没有响应，回退到 HTTP
        setTimeout(() => {
          if (editorStore.saveStatus === 'saving') {
            if (testingMode.value) console.warn('⚠️ WebSocket save timeout (5s), falling back to HTTP')
            saveViaHttp()
          }
        }, 5000)
      } catch (error) {
        if (testingMode.value) console.warn('❌ WebSocket save failed, falling back to HTTP:', error)
        await saveViaHttp()
      }
    } else {
      if (testingMode.value) {
        console.log('❌ WebSocket not available, using HTTP')
        console.log('WebSocket available:', !!ws)
        console.log('WebSocket state:', ws?.readyState)
      }
      await saveViaHttp()
    }
  }, 500)
}

const startRename = () => {
  renamingFile.value = true
  newFilename.value = displayName.value
  renameError.value = ''
  
  // 下一帧聚焦输入框
  nextTick(() => {
    renameInput.value?.focus()
    renameInput.value?.select()
  })
}

const cancelRename = () => {
  renamingFile.value = false
  newFilename.value = ''
  renameError.value = ''
}

const deleteFile = async () => {
  if (!confirm(`确定要删除文件 "${displayName.value}" 吗？此操作不可恢复。`)) {
    return
  }
  
  deletingFile.value = true
  
  try {
    await filesApi.deleteFile(editorStore.currentFile)
    
    // 删除成功，跳转到首页
    router.push('/')
  } catch (err: any) {
    console.error('Delete error:', err)
    alert(err.response?.data?.detail || '删除文件失败')
  } finally {
    deletingFile.value = false
  }
}

const testSave = async () => {
  if (testingMode.value) {
    console.log('=== Manual Test Save ===')
    console.log('Current file:', editorStore.currentFile)
    console.log('Content length:', editorStore.content.length)
    console.log('Content preview:', editorStore.content.substring(0, 100))
  }
  
  editorStore.setSaveStatus('saving')
  
  try {
    const response = await notesApi.saveFile(editorStore.currentFile, editorStore.content)
    if (testingMode.value) console.log('Test save response:', response)
    editorStore.setSaveStatus('saved')
    if (testingMode.value) console.log('✅ Test save successful!')
  } catch (error: any) {
    if (testingMode.value) {
      console.error('❌ Test save failed:', error)
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        headers: error.response?.headers
      })
    }
    editorStore.setSaveStatus('error')
  }
}

const toggleTestingMode = () => {
  testingMode.value = !testingMode.value
}

const confirmRename = async () => {
  if (!newFilename.value.trim()) {
    renameError.value = '文件名不能为空'
    return
  }
  
  // 验证文件名
  if (newFilename.value.length > 20) {
    renameError.value = '文件名不能超过20个字符'
    return
  }
  
  // 基本验证：不允许特殊字符
  const invalidChars = /[<>:"/\\|?*\x00-\x1f]/
  if (invalidChars.test(newFilename.value)) {
    renameError.value = '文件名包含无效字符'
    return
  }
  
  try {
    const oldFilename = editorStore.currentFile
    
    // 先断开当前WebSocket连接
    disconnect()
    
    await filesApi.renameFile(oldFilename, newFilename.value)
    
    // 重命名成功，更新当前文件名
    editorStore.setCurrentFile(newFilename.value)
    
    // 更新URL
    router.replace(`/notes/${newFilename.value}`)
    
    // 连接到新的WebSocket
    connect(newFilename.value)
    
    cancelRename()
  } catch (err: any) {
    console.error('Rename error:', err)
    renameError.value = err.response?.data?.detail || '重命名失败'
    
    // 重命名失败，重连到旧的WebSocket
    const oldFilename = editorStore.currentFile
    connect(oldFilename)
  }
}

const saveViaHttp = async () => {
  try {
    // 检查内容是否为空
    if (!editorStore.content || editorStore.content.trim() === '') {
      if (testingMode.value) console.log('Content is empty, deleting file:', editorStore.currentFile)
      await filesApi.deleteFile(editorStore.currentFile)
      editorStore.setSaveStatus('saved')
      if (testingMode.value) console.log('Empty file deleted successfully')
      return
    }
    
    if (testingMode.value) {
      console.log('Attempting HTTP save for:', editorStore.currentFile)
      console.log('Request payload:', { content: editorStore.content })
    }
    
    const response = await notesApi.saveFile(editorStore.currentFile, editorStore.content)
    if (testingMode.value) console.log('HTTP save response:', response)
    
    editorStore.setSaveStatus('saved')
    if (testingMode.value) console.log('HTTP save successful')
  } catch (error: any) {
    if (testingMode.value) {
      console.error('HTTP save failed:', error)
      console.error('Error response:', error.response)
      console.error('Error status:', error.response?.status)
      console.error('Error data:', error.response?.data)
    }
    
    editorStore.setSaveStatus('error')
    
    // 如果是网络错误，可以尝试重试
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      if (testingMode.value) console.log('Network error detected, retrying in 2 seconds...')
      setTimeout(() => {
        if (editorStore.saveStatus === 'error') {
          saveViaHttp()
        }
      }, 2000)
    }
  }
}

const loadFile = async (filename: string) => {
  editorStore.setLoading(true)
  editorStore.setCurrentFile(filename)
  
  try {
    const response = await notesApi.getFile(filename)
    editorStore.setContent(response.data.content)
    editorStore.setSaveStatus('saved')
  } catch (error) {
    console.error('Load failed:', error)
    editorStore.setContent('')
    editorStore.setSaveStatus('error')
  } finally {
    editorStore.setLoading(false)
  }
}

onMounted(() => {
  editorElement.value?.focus()
  const filename = route.params.filename as string
  loadFile(filename)
  connect(filename)
  
  // 监听来自FileListView的事件
  emitter.on('disconnect-websocket', () => {
    disconnect()
  })
  
  emitter.on('connect-websocket', (filename: string) => {
    connect(filename)
  })
})

onUnmounted(() => {
  disconnect()
  
  // 清理事件监听器
  emitter.off('disconnect-websocket', () => {})
  emitter.off('connect-websocket', () => {})
})

watch(() => route.params.filename, (newFilename) => {
  const filename = newFilename as string
  loadFile(filename)
  connect(filename)
})
</script>

<style scoped>
.editor-view {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #ecf0f1;
  background-color: #ffffff;
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.editor-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.editor-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.editor-textarea {
  flex: 1;
  border: none;
  padding: 1rem;
  font-family: 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  background-color: #ffffff;
  color: #2c3e50;
}

.editor-textarea:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-help {
  color: #7f8c8d;
  font-size: 12px;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.debug-tools {
  position: fixed;
  top: 10px;
  right: 10px;
  background-color: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 1rem;
  border-radius: 4px;
  z-index: 9999;
}

.debug-info {
  font-size: 12px;
  margin-top: 0.5rem;
}

.debug-info p {
  margin: 0;
  color: white;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .editor-header {
    padding: 0.75rem 1rem;
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .editor-title {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .editor-title h2 {
    font-size: 16px;
    text-align: center;
  }
  
  .editor-actions {
    justify-content: center;
    gap: 0.5rem;
  }
  
  .editor-actions .btn {
    flex: 1;
    font-size: 13px;
  }
  
  .editor-textarea {
    padding: 0.75rem;
    font-size: 13px;
  }
  
  .modal-content {
    margin: 1rem;
    padding: 1.5rem;
    width: calc(100% - 2rem);
  }
  
  .modal-content h3 {
    font-size: 18px;
  }
  
  .modal-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-actions .btn {
    width: 100%;
  }
  
  .debug-tools {
    position: fixed;
    top: 5px;
    right: 5px;
    left: 5px;
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .editor-header {
    padding: 0.5rem;
  }
  
  .editor-title h2 {
    font-size: 15px;
  }
  
  .editor-actions .btn {
    padding: 0.5rem 0.75rem;
    font-size: 12px;
  }
  
  .editor-textarea {
    padding: 0.5rem;
    font-size: 12px;
  }
  
  .modal-content {
    margin: 0.5rem;
    padding: 1rem;
  }
  
  .form-input {
    padding: 0.6rem;
    font-size: 14px;
  }
}
</style>