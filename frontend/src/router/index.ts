import { createRouter, createWebHistory } from 'vue-router'
import EditorView from '@/views/EditorView.vue'
import FileListView from '@/views/FileListView.vue'
import TestView from '@/views/TestView.vue'

const routes = [
  {
    path: '/notes/:filename',
    name: 'editor',
    component: EditorView,
    props: true
  },
  {
    path: '/list',
    name: 'list',
    component: FileListView
  },
  {
    path: '/test',
    name: 'test',
    component: TestView
  },
  {
    path: '/',
    redirect: () => {
      // 生成随机文件名
      const timestamp = Date.now().toString(36)
      const random = Math.random().toString(36).substr(2, 5)
      return `/notes/${timestamp}-${random}`
    }
  }]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router