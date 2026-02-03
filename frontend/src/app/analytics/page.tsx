'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

export default function Analytics() {
  const [scamTypes, setScamTypes] = useState<any[]>([])
  const [extractionRate, setExtractionRate] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAnalytics()
  }, [])

  const loadAnalytics = async () => {
    try {
      const [types, rate] = await Promise.all([
        api.get('/analytics/scam-types'),
        api.get('/analytics/extraction-rate')
      ])
      setScamTypes(types)
      setExtractionRate(rate)
    } catch (error) {
      console.error('Error loading analytics:', error)
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
        <h1 className="text-4xl font-bold mb-2">Analytics</h1>
        <p className="text-muted-foreground">
          Comprehensive analytics and insights
        </p>
      </div>

      {/* Extraction Rate */}
      {extractionRate && (
        <div className="bg-secondary rounded-lg p-6 border border-border">
          <h2 className="text-2xl font-bold mb-4">Intelligence Extraction Rate</h2>
          <div className="grid grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-muted-foreground mb-2">Total Scam Conversations</div>
              <div className="text-3xl font-bold">{extractionRate.total_scam_conversations}</div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground mb-2">With Intelligence</div>
              <div className="text-3xl font-bold text-green-500">
                {extractionRate.conversations_with_intelligence}
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground mb-2">Success Rate</div>
              <div className="text-3xl font-bold text-primary">
                {extractionRate.success_rate}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scam Types Distribution */}
      <div className="bg-secondary rounded-lg p-6 border border-border">
        <h2 className="text-2xl font-bold mb-4">Scam Type Distribution</h2>
        {scamTypes.length === 0 ? (
          <p className="text-muted-foreground">No data available</p>
        ) : (
          <div className="space-y-4">
            {scamTypes.map((item, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold">{item.type}</span>
                  <span className="text-muted-foreground">{item.count}</span>
                </div>
                <div className="w-full bg-background rounded-full h-3">
                  <div
                    className="bg-primary rounded-full h-3"
                    style={{
                      width: `${(item.count / Math.max(...scamTypes.map(s => s.count))) * 100}%`
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
