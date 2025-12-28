<template>
  <div class="file-list-view">
    <!-- 未认证时显示密码输入 -->
    <div v-if="!isAuthenticated" class="auth-container">
      <div class="auth-card">
        <h2>访问文件列表</h2>
        <p class="auth-description">请输入访问口令以查看文件列表</p>
        
        <form @submit.prevent="verifyPassword" class="auth-form">
          <div class="form-group">
            <label for="password">访问口令</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="请输入口令"
              class="form-input"
              required
            />
          </div>
          
          <button
            type="submit"
            class="btn btn-primary"
            :disabled="loading"
          >
            {{ loading ? '验证中...' : '验证' }}
          </button>
          
          <p v-if="error" class="error-message">{{ error }}</p>
        </form>
      </div>
    </div>
    
    <!-- 已认证时显示文件列表 -->
    <div v-else>
      <div class="file-list-header">
        <h1>文件列表</h1>
        <div class="header-right">
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索文件名..."
              class="search-input"
            />
            <button 
              v-if="searchQuery"
              @click="clearSearch"
              class="btn btn-secondary btn-sm"
            >
              清除
            </button>
          </div>
          <div class="header-actions">
            <RouterLink to="/" class="btn btn-primary">
                        新建文件
                      </RouterLink>            <button @click="logout" class="btn btn-secondary">
              退出
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button @click="fetchFiles" class="btn btn-secondary">重试</button>
      </div>
      
      <div v-else-if="filteredFiles.length === 0" class="empty-container">
        <p v-if="searchQuery">
          没有找到匹配 "{{ searchQuery }}" 的文件
        </p>
        <p v-else>
          还没有文件，创建您的第一个文件吧！
        </p>
        <RouterLink to="/" class="btn btn-primary">
          创建文件
        </RouterLink>
      </div>
      
      <div v-else class="file-list">
        <div
          v-for="file in filteredFiles"
          :key="file.filename"
          class="file-item"
        >
          <RouterLink
            :to="`/notes/${getDisplayName(file.filename)}`"
            class="file-link"
          >
            <div class="file-info">
              <div class="file-name">{{ getDisplayName(file.filename) }}</div>
              <div v-if="file.preview" class="file-preview">
                {{ file.preview }}
              </div>
              <div class="file-meta">
                创建时间: {{ formatDate(file.created_at) }} | 
                大小: {{ formatFileSize(file.size) }}
              </div>
            </div>
          </RouterLink>
          <div class="file-actions">
            <button
              @click.prevent="startRename(file.filename)"
              class="btn btn-secondary btn-sm"
            >
              重命名
            </button>
            <button
              @click.prevent="deleteFile(file.filename)"
              class="btn btn-danger btn-sm"
              :disabled="deleting === file.filename"
            >
              {{ deleting === file.filename ? '删除中...' : '删除' }}
            </button>
          </div>
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
                required
              />
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
                :disabled="!newFilename || renaming"
              >
                {{ renaming ? '重命名中...' : '确认' }}
              </button>
            </div>
          </form>
          <p v-if="renameError" class="error-message">{{ renameError }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { filesApi, type FileListItem } from '@/services/api'
import { emitter } from '@/utils/eventBus'

const router = useRouter()
const files = ref<FileListItem[]>([])
const filteredFiles = ref<FileListItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const searchQuery = ref('')
const deleting = ref<string | null>(null)
const renamingFile = ref<string | null>(null)
const newFilename = ref('')
const renaming = ref(false)
const renameError = ref<string | null>(null)
const renameInput = ref<HTMLInputElement>()
const isAuthenticated = ref(false)
const password = ref('')

const fetchFiles = async () => {
  loading.value = true
  error.value = null
  
  try {
    const response = await filesApi.getList()
    files.value = response.data.files
    filterFiles()
  } catch (err: any) {
    if (err.response?.status === 401) {
      // 需要认证
      isAuthenticated.value = false
    } else {
      error.value = err instanceof Error ? err.message : '获取文件列表失败'
    }
  } finally {
    loading.value = false
  }
}

const filterFiles = () => {
  if (!searchQuery.value.trim()) {
    filteredFiles.value = [...files.value]
  } else {
    const query = searchQuery.value.toLowerCase()
    filteredFiles.value = files.value.filter(file => 
      getDisplayName(file.filename).toLowerCase().includes(query)
    )
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  filterFiles()
}

const verifyPassword = async () => {
  if (!password.value) {
    error.value = '请输入口令'
    return
  }
  
  loading.value = true
  error.value = null
  
  try {
    const response = await filesApi.verifyPassword(password.value)
    localStorage.setItem('authToken', response.data.token)
    isAuthenticated.value = true
    await fetchFiles()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '口令验证失败'
  } finally {
    loading.value = false
  }
}

const logout = () => {
  localStorage.removeItem('authToken')
  isAuthenticated.value = false
  error.value = null
  files.value = []
}

const deleteFile = async (filename: string) => {
  if (!confirm(`确定要删除文件 "${filename}" 吗？此操作不可恢复。`)) {
    return
  }
  
  deleting.value = filename
  
  try {
    await filesApi.deleteFile(filename)
    // 从列表中移除文件
    files.value = files.value.filter(f => f.filename !== filename)
    // filterFiles 会自动更新 filteredFiles
  } catch (err: any) {
    error.value = err.response?.data?.detail || '删除文件失败'
  } finally {
    deleting.value = null
  }
}

const startRename = (filename: string) => {
  renamingFile.value = filename
  // 显示时不包含 .txt 后缀
  newFilename.value = getDisplayName(filename)
  renameError.value = null
  
  // 下一帧聚焦输入框
  nextTick(() => {
    renameInput.value?.focus()
    renameInput.value?.select()
  })
}

const cancelRename = () => {
  renamingFile.value = null
  newFilename.value = ''
  renameError.value = null
}

const confirmRename = async () => {
  if (!renamingFile.value || !newFilename.value) {
    return
  }
  
  renaming.value = true
  renameError.value = null
  
  try {
    // 确保传递给后端的文件名不包含.txt后缀
    const oldFilename = getDisplayName(renamingFile.value)
    
    // 如果当前正在编辑这个文件，先断开WebSocket连接
    const currentRoute = router.currentRoute.value
    const currentFilename = currentRoute.params.filename as string
    const isEditingCurrentFile = currentFilename === oldFilename
    
    if (isEditingCurrentFile) {
      // 通过事件总线通知编辑器断开WebSocket
      emitter.emit('disconnect-websocket')
    }
    
    await filesApi.renameFile(oldFilename, newFilename.value)
    
    // 更新列表中的文件名
    const fileIndex = files.value.findIndex(f => f.filename === renamingFile.value)
    if (fileIndex !== -1) {
      files.value[fileIndex].filename = `${newFilename.value}.txt`
    }
    
    // 如果当前正在编辑这个文件，导航到新的文件名
    if (isEditingCurrentFile) {
      router.push(`/editor/${newFilename.value}`)
      // 通过事件总线通知编辑器连接新的WebSocket
      emitter.emit('connect-websocket', newFilename.value)
    }
    
    cancelRename()
  } catch (err: any) {
    renameError.value = err.response?.data?.detail || '重命名失败'
    
    // 重命名失败，如果当前正在编辑这个文件，重连WebSocket
    const currentRoute = router.currentRoute.value
    const currentFilename = currentRoute.params.filename as string
    const oldFilename = getDisplayName(renamingFile.value)
    
    if (currentFilename === oldFilename) {
      // 通过事件总线通知编辑器重连WebSocket
      emitter.emit('connect-websocket', oldFilename)
    }
  } finally {
    renaming.value = false
  }
}

const checkAuth = () => {
  const token = localStorage.getItem('authToken')
  if (token) {
    isAuthenticated.value = true
    fetchFiles()
  }
}

// 监听搜索查询变化
watch(searchQuery, filterFiles)

// 监听文件列表变化
watch(files, filterFiles)

const formatDate = (date: string | Date) => {
  // 确保日期是有效的 Date 对象
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  // 检查日期是否有效
  if (isNaN(dateObj.getTime())) {
    return '未知时间'
  }
  
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(dateObj)
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getDisplayName = (filename: string) => {
  // 移除 .txt 后缀
  if (filename.toLowerCase().endsWith('.txt')) {
    return filename.slice(0, -4)
  }
  return filename
}

onMounted(() => {
  checkAuth()
})
</script>

<style scoped>
.file-list-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.auth-card {
  background-color: #ffffff;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.auth-card h2 {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.auth-description {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.file-list-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 250px;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.loading-container,
.error-container,
.empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-container p,
.error-container .error-message,
.empty-container p {
  margin-top: 1rem;
  color: #7f8c8d;
}

.error-message {
  color: #e74c3c;
}

.file-list {
  display: grid;
  gap: 1rem;
}

.file-item {
  border: 1px solid #ecf0f1;
  border-radius: 8px;
  background-color: #ffffff;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
  display: flex;
  align-items: center;
}

.file-item:hover {
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.1);
}

.file-link {
  flex: 1;
  padding: 1rem;
  text-decoration: none;
  color: inherit;
}

.file-actions {
  padding: 0 1rem;
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 12px;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #c0392b;
}

.file-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.file-name {
  font-size: 16px;
  font-weight: 500;
  color: #2c3e50;
}

.file-preview {
  font-size: 13px;
  color: #7f8c8d;
  margin-top: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-style: italic;
}

.file-meta {
  font-size: 12px;
  color: #7f8c8d;
  margin-top: 4px;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-block;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.header-actions {
  display: flex;
  gap: 1rem;
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

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .file-list-view {
    padding: 0.5rem;
  }
  
  .file-list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
    padding: 1rem;
  }
  
  .header-right {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-box {
    width: 100%;
  }
  
  .search-input {
    width: 100%;
    flex: 1;
  }
  
  .header-actions {
    width: 100%;
    justify-content: stretch;
    gap: 0.5rem;
  }
  
  .header-actions .btn {
    flex: 1;
  }
  
  .file-item {
    flex-direction: column;
    align-items: stretch;
  }
  
  .file-link {
    padding: 1rem;
  }
  
  .file-actions {
    padding: 0 1rem 1rem;
    justify-content: stretch;
    gap: 0.5rem;
  }
  
  .file-actions .btn {
    flex: 1;
  }
  
  .modal-content {
    margin: 1rem;
    padding: 1.5rem;
    width: calc(100% - 2rem);
  }
  
  .modal-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .modal-actions .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .file-list-view {
    padding: 0.25rem;
  }
  
  .file-list-header {
    padding: 0.75rem;
  }
  
  .file-list-header h1 {
    font-size: 20px;
  }
  
  .auth-card {
    margin: 0.5rem;
    padding: 1.5rem;
  }
  
  .file-link {
    padding: 0.75rem;
  }
  
  .file-name {
    font-size: 15px;
  }
  
  .file-preview {
    font-size: 12px;
  }
  
  .file-meta {
    font-size: 11px;
  }
  
  .btn {
    padding: 0.6rem 1rem;
    font-size: 13px;
  }
  
  .btn-sm {
    padding: 0.4rem 0.8rem;
    font-size: 11px;
  }
}
</style>