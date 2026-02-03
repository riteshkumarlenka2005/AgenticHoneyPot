'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface Stats {
  active_conversations: number
  scams_detected: number
  intelligence_extracted: number
  time_wasted_hours: number
}

interface Activity {
  timestamp: string
  scammer_identifier: string
  sender_type: string
  preview: string
  scam_type: string | null
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [statsData, activitiesData] = await Promise.all([
        api.get('/analytics/overview'),
        api.get('/analytics/recent-activity')
      ])
      setStats(statsData)
      setActivities(activitiesData)
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Real-time monitoring of honeypot activities
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-secondary rounded-lg p-6 border border-border">
          <div className="text-sm text-muted-foreground mb-2">Active Conversations</div>
          <div className="text-3xl font-bold text-primary">
            {stats?.active_conversations || 0}
          </div>
        </div>
        
        <div className="bg-secondary rounded-lg p-6 border border-border">
          <div className="text-sm text-muted-foreground mb-2">Scams Detected</div>
          <div className="text-3xl font-bold text-destructive">
            {stats?.scams_detected || 0}
          </div>
        </div>
        
        <div className="bg-secondary rounded-lg p-6 border border-border">
          <div className="text-sm text-muted-foreground mb-2">Intelligence Extracted</div>
          <div className="text-3xl font-bold text-green-500">
            {stats?.intelligence_extracted || 0}
          </div>
        </div>
        
        <div className="bg-secondary rounded-lg p-6 border border-border">
          <div className="text-sm text-muted-foreground mb-2">Time Wasted</div>
          <div className="text-3xl font-bold text-yellow-500">
            {stats?.time_wasted_hours || 0}h
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-secondary rounded-lg p-6 border border-border">
        <h2 className="text-2xl font-bold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {activities.length === 0 ? (
            <p className="text-muted-foreground">No recent activity</p>
          ) : (
            activities.map((activity, idx) => (
              <div
                key={idx}
                className="flex items-start gap-4 p-4 bg-background rounded border border-border"
              >
                <div
                  className={`w-2 h-2 mt-2 rounded-full ${
                    activity.sender_type === 'scammer' ? 'bg-destructive' : 'bg-primary'
                  }`}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold">{activity.scammer_identifier}</span>
                    {activity.scam_type && (
                      <span className="text-xs bg-destructive/20 text-destructive px-2 py-1 rounded">
                        {activity.scam_type}
                      </span>
                    )}
                    <span className="text-xs text-muted-foreground ml-auto">
                      {new Date(activity.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">{activity.preview}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
