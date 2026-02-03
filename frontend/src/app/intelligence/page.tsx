'use client'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'

interface IntelligenceItem {
  id: string
  conversation_id: string
  artifact_type: string
  value: string
  confidence: number
  extracted_at: string
  validated: boolean
}

export default function Intelligence() {
  const [intelligence, setIntelligence] = useState<IntelligenceItem[]>([])
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadIntelligence()
  }, [])

  const loadIntelligence = async () => {
    try {
      const [items, summaryData] = await Promise.all([
        api.get('/intelligence'),
        api.get('/intelligence/summary')
      ])
      setIntelligence(items)
      setSummary(summaryData)
    } catch (error) {
      console.error('Error loading intelligence:', error)
    } finally {
      setLoading(false)
    }
  }

  const exportData = async (format: string) => {
    try {
      const data = await api.get(`/intelligence/export?format=${format}`, true)
      const blob = new Blob([typeof data === 'string' ? data : JSON.stringify(data, null, 2)])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `intelligence.${format}`
      a.click()
    } catch (error) {
      console.error('Error exporting data:', error)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2">Intelligence</h1>
          <p className="text-muted-foreground">
            Extracted artifacts from scammer conversations
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => exportData('json')}
            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
          >
            Export JSON
          </button>
          <button
            onClick={() => exportData('csv')}
            className="px-4 py-2 bg-secondary text-secondary-foreground rounded hover:bg-secondary/90 border border-border"
          >
            Export CSV
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {Object.entries(summary).map(([type, data]: [string, any]) => (
            <div key={type} className="bg-secondary rounded-lg p-4 border border-border">
              <div className="text-sm text-muted-foreground mb-1">
                {type.replace('_', ' ').toUpperCase()}
              </div>
              <div className="text-2xl font-bold">{data.count}</div>
            </div>
          ))}
        </div>
      )}

      {/* Intelligence Table */}
      <div className="bg-secondary rounded-lg border border-border overflow-hidden">
        <table className="w-full">
          <thead className="bg-background border-b border-border">
            <tr>
              <th className="text-left p-4">Type</th>
              <th className="text-left p-4">Value</th>
              <th className="text-left p-4">Confidence</th>
              <th className="text-left p-4">Extracted At</th>
              <th className="text-left p-4">Validated</th>
            </tr>
          </thead>
          <tbody>
            {intelligence.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-center p-8 text-muted-foreground">
                  No intelligence extracted yet
                </td>
              </tr>
            ) : (
              intelligence.map((item) => (
                <tr key={item.id} className="border-b border-border hover:bg-background/50">
                  <td className="p-4">
                    <span className="px-2 py-1 rounded text-xs bg-primary/20 text-primary">
                      {item.artifact_type}
                    </span>
                  </td>
                  <td className="p-4 font-mono text-sm">{item.value}</td>
                  <td className="p-4">{(item.confidence * 100).toFixed(0)}%</td>
                  <td className="p-4 text-sm text-muted-foreground">
                    {new Date(item.extracted_at).toLocaleString()}
                  </td>
                  <td className="p-4">
                    {item.validated ? (
                      <span className="text-green-500">✓</span>
                    ) : (
                      <span className="text-gray-500">-</span>
                    )}
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
