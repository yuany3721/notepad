import { ref } from 'vue'
import { useEditorStore } from '@/stores/editor'

export function useWebSocket() {
  let ws: WebSocket | null = null
  const reconnectAttempts = ref(0)
  const maxReconnectAttempts = 5
  const editorStore = useEditorStore()
  
  const connect = (filename: string) => {
    if (ws) {
      ws.close()
    }
    
    // 使用相对路径，通过 Vite 代理
    const wsUrl = `/ws/${filename}`
    if (import.meta.env.DEV) console.log(`Connecting to WebSocket at: ${wsUrl}`)
    
    try {
      ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        reconnectAttempts.value = 0
        // 只在开发环境输出
        if (import.meta.env.DEV) console.log('WebSocket connected')
      }
      
      ws.onmessage = (event) => {
        // 只在开发环境输出
        if (import.meta.env.DEV) {
          console.log('📨 WebSocket message received:', event.data)
        }
        const message = JSON.parse(event.data)
        if (import.meta.env.DEV) {
          console.log('📨 Parsed message:', message)
        }
        handleMessage(message)
      }
      
      ws.onclose = (event) => {
        // 只在开发环境输出
        if (import.meta.env.DEV) console.log('WebSocket closed:', event.code, event.reason)
        if (reconnectAttempts.value < maxReconnectAttempts) {
          setTimeout(() => {
            reconnectAttempts.value++
            if (import.meta.env.DEV) console.log(`Reconnecting... attempt ${reconnectAttempts.value}`)
            connect(filename)
          }, 1000 * reconnectAttempts.value)
        } else {
          console.error('Max reconnection attempts reached')
          editorStore.setSaveStatus('error')
        }
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        editorStore.setSaveStatus('error')
      }
    } catch (error) {
      if (import.meta.env.DEV) console.error('Failed to create WebSocket:', error)
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
    }
  }
  
  const disconnect = () => {
    if (ws) {
      ws.close()
      ws = null
    }
  }
  
  const handleMessage = (message: any) => {
    if (import.meta.env.DEV) console.log('🔄 Handling WebSocket message:', message)
    switch (message.type) {
      case 'save_response':
        if (import.meta.env.DEV) console.log('✅ Save response received:', message.status)
        editorStore.setSaveStatus(
          message.status === 'success' ? 'saved' : 'error'
        )
        break
      case 'error':
        console.error('❌ WebSocket error:', message.message)
        editorStore.setSaveStatus('error')
        break
      default:
        if (import.meta.env.DEV) console.log('❓ Unknown message type:', message.type)
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