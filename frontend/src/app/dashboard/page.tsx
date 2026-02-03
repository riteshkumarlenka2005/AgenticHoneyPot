'use client'

import { useEffect, useState } from 'react'
import { api, OverviewStats } from '@/lib/api'
import { Sidebar } from '@/components/ui/sidebar'
import { StatCard } from '@/components/dashboard/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, AlertTriangle, Database, Clock } from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    // Refresh every 5 seconds
    const interval = setInterval(loadStats, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    const response = await api.getOverviewStats()
    if (response.data) {
      setStats(response.data)
      setLoading(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) return `${hours}h ${minutes}m`
    if (minutes > 0) return `${minutes}m`
    return `${seconds}s`
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Real-time overview of scam detection and intelligence extraction
            </p>
          </div>

          {/* Stats Grid */}
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                  </CardHeader>
                  <CardContent>
                    <div className="h-8 w-16 bg-muted animate-pulse rounded" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : stats ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="Active Conversations"
                value={stats.active_conversations}
                description="Currently engaging scammers"
                icon={<Activity className="h-4 w-4" />}
              />
              <StatCard
                title="Scams Detected"
                value={stats.scams_detected}
                description="Total scams identified"
                icon={<AlertTriangle className="h-4 w-4" />}
              />
              <StatCard
                title="Intelligence Extracted"
                value={stats.intelligence_extracted}
                description="Artifacts collected"
                icon={<Database className="h-4 w-4" />}
              />
              <StatCard
                title="Time Wasted"
                value={formatDuration(stats.time_wasted_seconds)}
                description="Scammer time consumed"
                icon={<Clock className="h-4 w-4" />}
              />
            </div>
          ) : null}

          {/* Activity Feed */}
          <div className="mt-8 grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Latest scammer interactions
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {!stats || stats.scams_detected === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-8">
                      No activity yet. Start by testing with the mock scammer.
                    </p>
                  ) : (
                    <p className="text-sm text-muted-foreground">
                      {stats.scams_detected} scam(s) detected and {stats.active_conversations} active conversation(s)
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common tasks and shortcuts
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <a
                    href="/conversations"
                    className="block p-3 rounded-lg border hover:bg-accent transition-colors"
                  >
                    <p className="font-medium">View Conversations</p>
                    <p className="text-sm text-muted-foreground">
                      See all active and completed honeypot sessions
                    </p>
                  </a>
                  <a
                    href="/intelligence"
                    className="block p-3 rounded-lg border hover:bg-accent transition-colors"
                  >
                    <p className="font-medium">Export Intelligence</p>
                    <p className="text-sm text-muted-foreground">
                      Download extracted scammer data
                    </p>
                  </a>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Getting Started */}
          {!stats || stats.scams_detected === 0 ? (
            <Card className="mt-8">
              <CardHeader>
                <CardTitle>Getting Started</CardTitle>
                <CardDescription>
                  Test the honeypot with a mock scammer
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="prose prose-sm max-w-none text-muted-foreground">
                  <ol className="list-decimal list-inside space-y-2">
                    <li>
                      Use the API to start a mock scammer session:
                      <code className="block mt-1 p-2 bg-muted rounded text-xs">
                        POST /api/v1/mock-scammer/start
                      </code>
                    </li>
                    <li>
                      Send the scammer message to the honeypot:
                      <code className="block mt-1 p-2 bg-muted rounded text-xs">
                        POST /api/v1/messages/incoming
                      </code>
                    </li>
                    <li>
                      Watch as the honeypot detects the scam and responds with a believable persona
                    </li>
                    <li>
                      View extracted intelligence on the Intelligence page
                    </li>
                  </ol>
                </div>
              </CardContent>
            </Card>
          ) : null}
        </div>
      </main>
    </div>
  )
}
