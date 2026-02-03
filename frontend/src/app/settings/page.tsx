'use client'

import { Sidebar } from '@/components/ui/sidebar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function SettingsPage() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
            <p className="text-muted-foreground">
              Configure honeypot behavior and preferences
            </p>
          </div>

          <div className="space-y-6 max-w-2xl">
            <Card>
              <CardHeader>
                <CardTitle>Detection Sensitivity</CardTitle>
                <CardDescription>
                  Configure how aggressively the system detects scams
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium">Minimum Confidence</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      defaultValue="50"
                      className="w-48"
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Messages with confidence below this threshold will not be engaged
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Persona Configuration</CardTitle>
                <CardDescription>
                  Manage honeypot personas and their behaviors
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">
                  4 active personas configured
                </p>
                <Button variant="outline">Manage Personas</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Safety Guardrails</CardTitle>
                <CardDescription>
                  Safety limits and restrictions (view only)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Max Conversation Duration</span>
                    <span>3600 seconds</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Max Messages per Conversation</span>
                    <span>100 messages</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Minimum Scam Confidence</span>
                    <span>50%</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-4">
                  These limits are enforced to ensure safe operation
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>API Configuration</CardTitle>
                <CardDescription>
                  OpenAI and external service settings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">OpenAI API Key</label>
                    <input
                      type="password"
                      placeholder="sk-..."
                      className="mt-1 w-full px-3 py-2 border rounded-md bg-background"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Model</label>
                    <select className="mt-1 w-full px-3 py-2 border rounded-md bg-background">
                      <option>gpt-4-turbo-preview</option>
                      <option>gpt-4</option>
                      <option>gpt-3.5-turbo</option>
                    </select>
                  </div>
                  <Button>Save Configuration</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
