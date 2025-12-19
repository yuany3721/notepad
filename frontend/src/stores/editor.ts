import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useEditorStore = defineStore('editor', () => {
  const currentFile = ref<string>('')
  const content = ref<string>('')
  const saveStatus = ref<'saved' | 'saving' | 'error'>('saved')
  const lastSaved = ref<Date | null>(null)
  const isLoading = ref(false)
  
  const setContent = (newContent: string) => {
    content.value = newContent
  }
  
  const setSaveStatus = (status: 'saved' | 'saving' | 'error') => {
    saveStatus.value = status
    if (status === 'saved') {
      lastSaved.value = new Date()
    }
  }
  
  const setLoading = (loading: boolean) => {
    isLoading.value = loading
  }
  
  const setCurrentFile = (filename: string) => {
    currentFile.value = filename
  }
  
  return {
    currentFile,
    content,
    saveStatus,
    lastSaved,
    isLoading,
    setContent,
    setSaveStatus,
    setLoading,
    setCurrentFile
  }
})