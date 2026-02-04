'use client'

import { io, Socket } from 'socket.io-client'

export type WebSocketEvent = 'message' | 'conversation' | 'intelligence' | 'connect' | 'disconnect' | 'error'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp: string
}

class WebSocketClient {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventHandlers: Map<WebSocketEvent, Set<Function>> = new Map()

  constructor() {
    // Initialize event handler sets
    const events: WebSocketEvent[] = ['message', 'conversation', 'intelligence', 'connect', 'disconnect', 'error']
    events.forEach(event => {
      this.eventHandlers.set(event, new Set())
    })
  }

  connect(url: string = 'http://localhost:8000'): void {
    if (this.socket?.connected) {
      console.log('WebSocket already connected')
      return
    }

    this.socket = io(url, {
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    })

    this.setupEventListeners()
  }

  private setupEventListeners(): void {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.emit('connect', null)
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.emit('disconnect', { reason })
      
      if (reason === 'io server disconnect') {
        // Server disconnected, attempt manual reconnection
        this.attemptReconnect()
      }
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
      this.emit('error', { error })
    })

    // Custom event handlers
    this.socket.on('new_message', (data) => {
      this.emit('message', data)
    })

    this.socket.on('conversation_update', (data) => {
      this.emit('conversation', data)
    })

    this.socket.on('intelligence_extracted', (data) => {
      this.emit('intelligence', data)
    })
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

    setTimeout(() => {
      this.socket?.connect()
    }, this.reconnectDelay * this.reconnectAttempts)
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  on(event: WebSocketEvent, handler: Function): () => void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.add(handler)
    }

    // Return cleanup function
    return () => {
      const handlers = this.eventHandlers.get(event)
      if (handlers) {
        handlers.delete(handler)
      }
    }
  }

  private emit(event: WebSocketEvent, data: any): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in ${event} handler:`, error)
        }
      })
    }
  }

  send(event: string, data: any): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected. Message not sent.')
      return
    }

    this.socket.emit(event, data)
  }

  isConnected(): boolean {
    return this.socket?.connected || false
  }
}

// Global WebSocket instance
export const websocket = new WebSocketClient()

// Hook for React components
export function useWebSocket() {
  return websocket
}
