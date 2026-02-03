/**
 * API client for the Agentic HoneyPot backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
export interface OverviewStats {
  active_conversations: number
  scams_detected: number
  intelligence_extracted: number
  time_wasted_seconds: number
}

export interface Conversation {
  id: string
  scammer_identifier: string
  status: 'active' | 'stalling' | 'completed' | 'abandoned'
  scam_type: string | null
  detection_confidence: number
  started_at: string
  message_count: number
  duration_seconds: number
}

export interface IntelligenceArtifact {
  id: string
  conversation_id: string
  artifact_type: 'upi_id' | 'bank_account' | 'ifsc_code' | 'phone' | 'url' | 'email'
  value: string
  confidence: number
  extracted_at: string
  validated: boolean
}

export interface ScamTypeDistribution {
  scam_type: string
  count: number
  percentage: number
}

export interface Message {
  id: string
  conversation_id: string
  sender_type: 'scammer' | 'honeypot'
  content: string
  timestamp: string
  analysis: Record<string, unknown>
}

export interface ApiResponse<T> {
  data: T | null
  error: string | null
}

// Helper function for API requests
async function request<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const error = await response.text()
      return { data: null, error: error || `HTTP ${response.status}` }
    }

    const data = await response.json()
    return { data, error: null }
  } catch (error) {
    return { data: null, error: error instanceof Error ? error.message : 'Unknown error' }
  }
}

// API client
export const api = {
  // Analytics
  async getOverviewStats(): Promise<ApiResponse<OverviewStats>> {
    return request<OverviewStats>('/api/v1/analytics/overview')
  },

  async getScamTypeDistribution(): Promise<ApiResponse<ScamTypeDistribution[]>> {
    return request<ScamTypeDistribution[]>('/api/v1/analytics/scam-types')
  },

  // Conversations
  async getConversations(params?: {
    limit?: number
    offset?: number
    status?: string
  }): Promise<ApiResponse<Conversation[]>> {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set('limit', String(params.limit))
    if (params?.offset) searchParams.set('offset', String(params.offset))
    if (params?.status) searchParams.set('status', params.status)
    
    const query = searchParams.toString()
    return request<Conversation[]>(`/api/v1/conversations${query ? `?${query}` : ''}`)
  },

  async getConversation(id: string): Promise<ApiResponse<Conversation>> {
    return request<Conversation>(`/api/v1/conversations/${id}`)
  },

  async getConversationMessages(id: string): Promise<ApiResponse<Message[]>> {
    return request<Message[]>(`/api/v1/conversations/${id}/messages`)
  },

  // Intelligence
  async getIntelligence(params?: {
    limit?: number
    artifact_type?: string
  }): Promise<ApiResponse<IntelligenceArtifact[]>> {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set('limit', String(params.limit))
    if (params?.artifact_type) searchParams.set('artifact_type', params.artifact_type)
    
    const query = searchParams.toString()
    return request<IntelligenceArtifact[]>(`/api/v1/intelligence${query ? `?${query}` : ''}`)
  },

  async exportIntelligence(format: 'json' | 'csv'): Promise<Blob | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/intelligence/export?format=${format}`)
      if (!response.ok) return null
      return await response.blob()
    } catch {
      return null
    }
  },

  // Messages
  async sendIncomingMessage(message: string, scammer_identifier: string): Promise<ApiResponse<{
    conversation_id: string
    honeypot_response: string
    scam_detected: boolean
    confidence: number
    scam_type: string
    engagement_phase: string
  }>> {
    return request('/api/v1/messages/incoming', {
      method: 'POST',
      body: JSON.stringify({ message, scammer_identifier }),
    })
  },

  // Mock Scammer
  async startMockSession(scenario: string): Promise<ApiResponse<{
    session_id: string
    initial_message: string
  }>> {
    return request('/api/v1/mock-scammer/start', {
      method: 'POST',
      body: JSON.stringify({ scenario }),
    })
  },

  async continueMockSession(session_id: string, response: string): Promise<ApiResponse<{
    scammer_reply: string
    session_ended: boolean
  }>> {
    return request('/api/v1/mock-scammer/continue', {
      method: 'POST',
      body: JSON.stringify({ session_id, response }),
    })
  },

  // Health
  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    return request<{ status: string }>('/health')
  },
}

export default api
