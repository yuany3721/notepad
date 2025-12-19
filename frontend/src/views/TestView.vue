<template>
  <div class="test-view">
    <h1>WebSocket 测试</h1>
    <div class="test-controls">
      <button @click="testWebSocket">测试 WebSocket 连接</button>
      <button @click="testHttpApi">测试 HTTP API</button>
    </div>
    <div class="test-results">
      <h3>测试结果：</h3>
      <pre>{{ results }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { notesApi } from '@/services/api'
import { useWebSocket } from '@/services/websocket'

const results = ref('')
const { connect, disconnect, sendSave } = useWebSocket()

const testWebSocket = async () => {
  results.value = '开始测试 WebSocket...\n'
  
  try {
    // 测试连接
    connect('test-websocket.txt')
    results.value += 'WebSocket 连接已尝试\n'
    
    // 测试发送消息
    setTimeout(() => {
      sendSave('test-websocket.txt', 'WebSocket 测试内容')
      results.value += 'WebSocket 消息已发送\n'
    }, 1000)
    
    // 5秒后断开
    setTimeout(() => {
      disconnect()
      results.value += 'WebSocket 已断开\n'
    }, 5000)
  } catch (error) {
    results.value += `WebSocket 错误: ${error}\n`
  }
}

const testHttpApi = async () => {
  results.value = '开始测试 HTTP API...\n'
  
  try {
    // 测试保存文件
    const saveResponse = await notesApi.saveFile('test-http.txt', 'HTTP API 测试内容')
    results.value += `保存成功: ${JSON.stringify(saveResponse.data, null, 2)}\n`
    
    // 测试读取文件
    const getResponse = await notesApi.getFile('test-http.txt')
    results.value += `读取成功: ${JSON.stringify(getResponse.data, null, 2)}\n`
  } catch (error) {
    results.value += `HTTP API 错误: ${error}\n`
  }
}
</script>

<style scoped>
.test-view {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.test-controls {
  margin: 1rem 0;
}

.test-controls button {
  margin-right: 1rem;
  padding: 0.5rem 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.test-controls button:hover {
  background-color: #2980b9;
}

.test-results {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>