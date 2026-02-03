'use client'

import { useEffect, useState } from 'react'
import { api, Conversation } from '@/lib/api'
import { Sidebar } from '@/components/ui/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadConversations()
    const interval = setInterval(loadConversations, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadConversations = async () => {
    const response = await api.getConversations({ limit: 50 })
    if (response.data) {
      setConversations(response.data)
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'stalling': return 'bg-yellow-500'
      case 'completed': return 'bg-blue-500'
      case 'abandoned': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    if (minutes > 60) {
      const hours = Math.floor(minutes / 60)
      return `${hours}h ${minutes % 60}m`
    }
    return `${minutes}m`
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Conversations</h1>
            <p className="text-muted-foreground">
              View and manage all honeypot conversations
            </p>
          </div>

          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <div className="h-6 w-48 bg-muted animate-pulse rounded mb-2" />
                    <div className="h-4 w-32 bg-muted animate-pulse rounded" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <p className="text-muted-foreground">
                  No conversations yet. Send a message to start engaging scammers.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {conversations.map((conv) => (
                <Card key={conv.id} className="hover:border-primary cursor-pointer transition-colors">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold">
                            {conv.scammer_identifier}
                          </h3>
                          <span className={`w-2 h-2 rounded-full ${getStatusColor(conv.status)}`} />
                          <span className="text-sm text-muted-foreground capitalize">
                            {conv.status}
                          </span>
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span>
                            Type: <span className="text-foreground">{conv.scam_type.replace('_', ' ')}</span>
                          </span>
                          <span>•</span>
                          <span>
                            Confidence: <span className="text-foreground">{(conv.detection_confidence * 100).toFixed(0)}%</span>
                          </span>
                          <span>•</span>
                          <span>
                            Messages: <span className="text-foreground">{conv.message_count}</span>
                          </span>
                          <span>•</span>
                          <span>
                            Duration: <span className="text-foreground">{formatDuration(conv.duration_seconds)}</span>
                          </span>
                        </div>
                      </div>
                      
                      <div className="text-sm text-muted-foreground">
                        {new Date(conv.started_at).toLocaleString()}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
