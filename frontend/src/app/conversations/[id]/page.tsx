'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { api } from '@/lib/api'

interface Message {
  id: string
  sender_type: string
  content: string
  timestamp: string
  analysis: any
}

interface ConversationDetail {
  id: string
  scammer_identifier: string
  status: string
  scam_type: string | null
  detection_confidence: number | null
  started_at: string
  last_activity: string
  messages: Message[]
}

export default function ConversationDetail() {
  const params = useParams()
  const router = useRouter()
  const [conversation, setConversation] = useState<ConversationDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (params.id) {
      loadConversation()
    }
  }, [params.id])

  const loadConversation = async () => {
    try {
      const data = await api.get(`/conversations/${params.id}`)
      setConversation(data)
    } catch (error) {
      console.error('Error loading conversation:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!conversation) {
    return <div className="text-center py-12">Conversation not found</div>
  }

  return (
    <div className="space-y-8">
      <div>
        <button
          onClick={() => router.back()}
          className="text-primary hover:underline mb-4"
        >
          ← Back to Conversations
        </button>
        <h1 className="text-4xl font-bold mb-2">Conversation Details</h1>
        <div className="flex gap-4 text-sm text-muted-foreground">
          <span>Scammer: {conversation.scammer_identifier}</span>
          <span>•</span>
          <span>Status: {conversation.status}</span>
          {conversation.scam_type && (
            <>
              <span>•</span>
              <span>Type: {conversation.scam_type}</span>
            </>
          )}
        </div>
      </div>

      <div className="bg-secondary rounded-lg p-6 border border-border space-y-4">
        {conversation.messages.map((msg) => (
          <div
            key={msg.id}
            className={`p-4 rounded-lg ${
              msg.sender_type === 'scammer'
                ? 'bg-destructive/10 border-l-4 border-destructive'
                : 'bg-primary/10 border-l-4 border-primary'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="font-semibold">
                {msg.sender_type === 'scammer' ? '🚨 Scammer' : '🍯 HoneyPot'}
              </span>
              <span className="text-xs text-muted-foreground">
                {new Date(msg.timestamp).toLocaleString()}
              </span>
            </div>
            <p className="whitespace-pre-wrap">{msg.content}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
