import { ref } from 'vue'
import { useEditorStore } from '@/stores/editor'

export function useWebSocket() {
  let ws: WebSocket | null = null
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const editorStore = useEditorStore()
  let reconnectTimeout: number | null = null
  let currentFilename = ''
  let isConnecting = false
  let usePolling = false
  let pollInterval: number | null = null
  
  const connect = (filename: string) => {
    if (isConnecting && currentFilename === filename) return
    
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    
    if (ws) {
      const oldWs = ws
      ws = null
      oldWs.onclose = null
      oldWs.close()
    }
    
    currentFilename = filename
    isConnecting = false
    usePolling = false
    
    const apiBaseURL = import.meta.env.VITE_API_BASE_URL || 'https://api.yuany3721.site'
    let wsUrl: string
    
    if (apiBaseURL.startsWith('/')) {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      wsUrl = `${protocol}//${host}/notepad/ws/${filename}`
    } else {
      const wsHost = import.meta.env.VITE_WS_HOST || apiBaseURL.replace(/^https?:\/\//, '')
      const protocol = apiBaseURL.startsWith('https:') ? 'wss:' : 'ws:'
      wsUrl = `${protocol}//${wsHost}/notepad/ws/${filename}`
    }
    
    try {
      isConnecting = true
      ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        reconnectAttempts.value = 0
        isConnecting = false
      }
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data)
        handleMessage(message)
      }
      
      ws.onclose = (event) => {
        isConnecting = false
        
        if (currentFilename === filename && reconnectAttempts.value < maxReconnectAttempts) {
          reconnectTimeout = window.setTimeout(() => {
            reconnectAttempts.value++
            connect(filename)
          }, 1000 * reconnectAttempts.value)
        }
      }
      
      ws.onerror = (error) => {
        isConnecting = false
        editorStore.setSaveStatus('error')
      }
    } catch (error) {
      isConnecting = false
      editorStore.setSaveStatus('error')
    }
  }
  
  const startPolling = (filename: string) => {
    usePolling = true
    reconnectAttempts.value = 0
    
    pollInterval = window.setInterval(() => {
      checkFileStatus(filename)
    }, 5000)
  }
  
  const stopPolling = () => {
    if (pollInterval) {
      clearInterval(pollInterval)
      pollInterval = null
    }
    usePolling = false
  }
  
  const checkFileStatus = async (filename: string) => {
    try {
      const response = await fetch(`/api/notepad/notes/${filename}`)
      if (response.ok) {
        const data = await response.json()
        if (data.content !== editorStore.content) {
          editorStore.setContent(data.content)
        }
      }
    } catch (error) {
      console.error('Polling error:', error)
    }
  }
  
  const saveViaHttp = async (filename: string, content: string) => {
    try {
      const response = await fetch(`/api/notepad/notes/${filename}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content })
      })
      
      if (response.ok) {
        const mockResponse = {
          type: 'save_response',
          status: 'success',
          message: '保存成功',
          timestamp: new Date().toISOString()
        }
        handleMessage(mockResponse)
      } else {
        throw new Error('HTTP save failed')
      }
    } catch (error) {
      console.error('HTTP save error:', error)
      editorStore.setSaveStatus('error')
    }
  }
  
  const sendSave = (filename: string, content: string) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'save',
        content,
        timestamp: new Date().toISOString()
      }))
    } else if (usePolling) {
      saveViaHttp(filename, content)
    } else {
      startPolling(filename)
      saveViaHttp(filename, content)
    }
  }
  
  const disconnect = () => {
    if (reconnectTimeout) {
      clearTimeout(reconnectTimeout)
      reconnectTimeout = null
    }
    
    if (ws) {
      ws.onclose = null
      ws.close()
      ws = null
    }
    
    stopPolling()
    
    isConnecting = false
    currentFilename = ''
  }
  
  const handleMessage = (message: any) => {
    switch (message.type) {
    case 'save_response':
      editorStore.setSaveStatus(
        message.status === 'success' ? 'saved' : 'error'
      )
      break
    case 'error':
      console.error('WebSocket error:', message.message)
      editorStore.setSaveStatus('error')
      break
    }
  }
  
  const getWebSocket = () => ws
  
  return {
    connect,
    sendSave,
    disconnect,
    getWebSocket
  }
}