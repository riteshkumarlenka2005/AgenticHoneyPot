'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { Sidebar } from '@/components/ui/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { MessageCircle, User, Clock, TrendingUp } from 'lucide-react'

interface Message {
  id: string
  sender_type: 'scammer' | 'honeypot'
  content: string
  timestamp: string
}

interface Intelligence {
  id: string
  artifact_type: string
  value: string
  confidence: number
}

interface Conversation {
  id: string
  scammer_identifier: string
  status: string
  scam_type: string
  detection_confidence: number
  started_at: string
  message_count: number
  duration_seconds: number
}

export default function ConversationDetailPage() {
  const params = useParams()
  const conversationId = params?.id as string
  
  const [conversation, setConversation] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [intelligence, setIntelligence] = useState<Intelligence[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (conversationId) {
      loadConversation()
    }
  }, [conversationId])

  const loadConversation = async () => {
    try {
      // Fetch conversation details
      const convRes = await fetch(`http://localhost:8000/api/v1/conversations/${conversationId}`)
      const convData = await convRes.json()
      setConversation(convData)

      // Fetch messages
      const msgRes = await fetch(`http://localhost:8000/api/v1/messages?conversation_id=${conversationId}`)
      const msgData = await msgRes.json()
      setMessages(msgData.messages || [])

      // Fetch intelligence
      const intRes = await fetch(`http://localhost:8000/api/v1/intelligence?conversation_id=${conversationId}`)
      const intData = await intRes.json()
      setIntelligence(intData.data || [])

      setLoading(false)
    } catch (error) {
      console.error('Error loading conversation:', error)
      setLoading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`
    }
    return `${minutes}m`
  }

  if (loading) {
    return (
      <div className="flex h-screen bg-background">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-8">
            <div className="text-center">Loading...</div>
          </div>
        </main>
      </div>
    )
  }

  if (!conversation) {
    return (
      <div className="flex h-screen bg-background">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <div className="container mx-auto p-8">
            <div className="text-center">Conversation not found</div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Conversation Details</h1>
            <p className="text-muted-foreground">
              {conversation.scammer_identifier}
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid gap-4 md:grid-cols-4 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Status</CardTitle>
                <User className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <Badge className="capitalize">{conversation.status}</Badge>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Messages</CardTitle>
                <MessageCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{conversation.message_count}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Duration</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatDuration(conversation.duration_seconds)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Confidence</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(conversation.detection_confidence * 100).toFixed(0)}%
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            {/* Messages */}
            <div className="md:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Message Thread</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-h-[600px] overflow-y-auto">
                    {messages.map((msg) => (
                      <div
                        key={msg.id}
                        className={`p-4 rounded-lg ${
                          msg.sender_type === 'scammer'
                            ? 'bg-red-50 border-l-4 border-red-500'
                            : 'bg-blue-50 border-l-4 border-blue-500'
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={msg.sender_type === 'scammer' ? 'destructive' : 'default'}>
                            {msg.sender_type}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(msg.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm">{msg.content}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Intelligence Sidebar */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Extracted Intelligence</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {intelligence.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No intelligence extracted yet</p>
                    ) : (
                      intelligence.map((item) => (
                        <div key={item.id} className="p-3 rounded-lg border">
                          <div className="text-xs text-muted-foreground mb-1 capitalize">
                            {item.artifact_type.replace('_', ' ')}
                          </div>
                          <div className="font-mono text-sm mb-1">{item.value}</div>
                          <div className="text-xs text-muted-foreground">
                            {(item.confidence * 100).toFixed(0)}% confidence
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="mt-4">
                <CardHeader>
                  <CardTitle>Scam Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div>
                      <div className="text-muted-foreground">Type</div>
                      <div className="font-medium capitalize">
                        {conversation.scam_type?.replace('_', ' ') || 'Unknown'}
                      </div>
                    </div>
                    <div>
                      <div className="text-muted-foreground">Started</div>
                      <div className="font-medium">
                        {new Date(conversation.started_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
