'use client'

import { useEffect, useState } from 'react'
import { api, IntelligenceArtifact } from '@/lib/api'
import { Sidebar } from '@/components/ui/sidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Download, Database, Phone, CreditCard, Link as LinkIcon, Mail } from 'lucide-react'

export default function IntelligencePage() {
  const [intelligence, setIntelligence] = useState<IntelligenceArtifact[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadIntelligence()
    const interval = setInterval(loadIntelligence, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadIntelligence = async () => {
    const response = await api.getIntelligence()
    if (response.data) {
      setIntelligence(response.data)
      setLoading(false)
    }
  }

  const handleExport = async (format: 'json' | 'csv') => {
    const data = await api.exportIntelligence(format)
    const blob = new Blob(
      [typeof data === 'string' ? data : JSON.stringify(data, null, 2)],
      { type: format === 'csv' ? 'text/csv' : 'application/json' }
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `intelligence.${format}`
    a.click()
  }

  const getIcon = (type: string) => {
    switch (type) {
      case 'upi_id': return <Database className="h-4 w-4" />
      case 'bank_account': return <CreditCard className="h-4 w-4" />
      case 'phone': return <Phone className="h-4 w-4" />
      case 'url': return <LinkIcon className="h-4 w-4" />
      case 'email': return <Mail className="h-4 w-4" />
      default: return <Database className="h-4 w-4" />
    }
  }

  const groupByType = () => {
    const grouped: Record<string, IntelligenceArtifact[]> = {}
    intelligence.forEach((item) => {
      if (!grouped[item.artifact_type]) {
        grouped[item.artifact_type] = []
      }
      grouped[item.artifact_type].push(item)
    })
    return grouped
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Intelligence</h1>
              <p className="text-muted-foreground">
                Extracted scammer artifacts and intelligence
              </p>
            </div>
            
            <div className="flex gap-2">
              <Button onClick={() => handleExport('json')} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
              <Button onClick={() => handleExport('csv')} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
            </div>
          </div>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <Card key={i}>
                  <CardHeader>
                    <div className="h-5 w-32 bg-muted animate-pulse rounded" />
                  </CardHeader>
                  <CardContent>
                    <div className="h-4 w-full bg-muted animate-pulse rounded" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : intelligence.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Database className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  No intelligence extracted yet. Start conversations to collect scammer data.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {Object.entries(groupByType()).map(([type, items]) => (
                <Card key={type}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      {getIcon(type)}
                      <span className="capitalize">{type.replace('_', ' ')}</span>
                      <span className="text-sm text-muted-foreground font-normal">
                        ({items.length})
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-3">
                      {items.map((item) => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-3 rounded-lg border"
                        >
                          <div className="flex-1">
                            <p className="font-mono text-sm">{item.value}</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              Confidence: {(item.confidence * 100).toFixed(0)}% •{' '}
                              {new Date(item.extracted_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      ))}
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
