import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000
})

// 请求拦截器 - 添加认证令牌
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 令牌过期，清除本地存储
      localStorage.removeItem('authToken')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export interface TextFile {
  filename: string
  content: string
  created_at: string
  updated_at: string
  size: number
}

export interface FileListItem {
  filename: string
  created_at: string
  size: number
}

export interface AuthToken {
  token: string
  expires_at: string
}

export interface FileListResponse {
  files: FileListItem[]
  total: number
  page: number
  limit: number
}

export const notesApi = {
  getFile: (filename: string) => api.get<TextFile>(`/notes/${filename}`),
  saveFile: (filename: string, content: string) => 
    api.post<TextFile>(`/notes/${filename}`, { content })
}

export const filesApi = {
  getList: (page = 1, limit = 50) => 
    api.get<FileListResponse>(
      '/files/list', { params: { page, limit } }
    ),
  verifyPassword: (password: string) => 
    api.post<AuthToken>('/files/verify-password', { password }),
  deleteFile: (filename: string) => 
    api.delete(`/files/${filename}`),
  renameFile: (filename: string, newFilename: string) => 
    api.put(`/files/${filename}/rename?new_filename=${encodeURIComponent(newFilename)}`)
}

export default api