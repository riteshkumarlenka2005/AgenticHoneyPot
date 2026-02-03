'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { api } from '@/lib/api'

interface Conversation {
  id: string
  scammer_identifier: string
  status: string
  scam_type: string | null
  detection_confidence: number | null
  started_at: string
  message_count: number
}

export default function Conversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadConversations()
    const interval = setInterval(loadConversations, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadConversations = async () => {
    try {
      const data = await api.get('/conversations')
      setConversations(data)
    } catch (error) {
      console.error('Error loading conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Conversations</h1>
        <p className="text-muted-foreground">
          All honeypot conversations with scammers
        </p>
      </div>

      <div className="bg-secondary rounded-lg border border-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-background border-b border-border">
            <tr>
              <th className="text-left p-4">Scammer ID</th>
              <th className="text-left p-4">Status</th>
              <th className="text-left p-4">Scam Type</th>
              <th className="text-left p-4">Confidence</th>
              <th className="text-left p-4">Messages</th>
              <th className="text-left p-4">Started</th>
              <th className="text-left p-4">Actions</th>
            </tr>
          </thead>
          <tbody>
            {conversations.length === 0 ? (
              <tr>
                <td colSpan={7} className="text-center p-8 text-muted-foreground">
                  No conversations yet
                </td>
              </tr>
            ) : (
              conversations.map((conv) => (
                <tr key={conv.id} className="border-b border-border hover:bg-background/50">
                  <td className="p-4 font-mono text-sm">{conv.scammer_identifier}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs ${
                      conv.status === 'active' ? 'bg-green-500/20 text-green-500' :
                      conv.status === 'stalling' ? 'bg-yellow-500/20 text-yellow-500' :
                      'bg-gray-500/20 text-gray-500'
                    }`}>
                      {conv.status}
                    </span>
                  </td>
                  <td className="p-4">{conv.scam_type || '-'}</td>
                  <td className="p-4">
                    {conv.detection_confidence 
                      ? `${(conv.detection_confidence * 100).toFixed(0)}%`
                      : '-'
                    }
                  </td>
                  <td className="p-4">{conv.message_count}</td>
                  <td className="p-4 text-sm text-muted-foreground">
                    {new Date(conv.started_at).toLocaleString()}
                  </td>
                  <td className="p-4">
                    <Link
                      href={`/conversations/${conv.id}`}
                      className="text-primary hover:underline text-sm"
                    >
                      View →
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
