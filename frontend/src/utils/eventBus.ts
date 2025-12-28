import { createApp } from 'vue'

type EventHandler = (...args: any[]) => void

class EventBus {
  private events: Record<string, EventHandler[]> = {}

  on(event: string, handler: EventHandler) {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(handler)
  }

  off(event: string, handler: EventHandler) {
    if (!this.events[event]) return
    const index = this.events[event].indexOf(handler)
    if (index > -1) {
      this.events[event].splice(index, 1)
    }
  }

  emit(event: string, ...args: any[]) {
    if (!this.events[event]) return
    this.events[event].forEach(handler => {
      handler(...args)
    })
  }
}

export const emitter = new EventBus()