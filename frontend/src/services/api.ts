import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://api.yuany3721.site',
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
      // 只在非密码验证页面刷新
      if (!error.config.url?.includes('verify-password')) {
        window.location.reload()
      }
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
  preview?: string
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
  getFile: (filename: string) => api.get<TextFile>(`/notepad/notes/${filename}`),
  saveFile: (filename: string, content: string) =>
    api.post<TextFile>(`/notepad/notes/${filename}`, { content })
}

export const filesApi = {
  getList: (page = 1, limit = 50) =>
    api.get<FileListResponse>(
      '/notepad/files/list', { params: { page, limit } }
    ),
  verifyPassword: (password: string) =>
    api.post<AuthToken>('/notepad/files/verify-password', { password }),
  deleteFile: (filename: string) =>
    api.post(`/notepad/files/${filename}/delete`),
  renameFile: (filename: string, newFilename: string) =>
    api.post(`/notepad/files/${filename}/rename?new_filename=${encodeURIComponent(newFilename)}`)
}

export default api