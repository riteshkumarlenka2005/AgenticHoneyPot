import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Book, Code, Zap, Shield } from 'lucide-react'

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-12">
            <h1 className="text-4xl font-bold mb-4">Documentation</h1>
            <p className="text-lg text-muted-foreground">
              Learn how to use Agentic HoneyPot to detect scams and extract intelligence
            </p>
          </div>

          {/* Quick Start */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-primary" />
                Quick Start Guide
              </CardTitle>
              <CardDescription>Get up and running in minutes</CardDescription>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none dark:prose-invert">
              <h3>1. Create an Account</h3>
              <p>Sign up for a free account to access the dashboard and start detecting scams.</p>
              
              <h3>2. Configure Your Settings</h3>
              <p>Set up your preferences in the Settings page, including detection sensitivity and persona types.</p>
              
              <h3>3. Start Testing</h3>
              <p>Use our mock scammer feature to test the system, or integrate with your messaging platforms.</p>
            </CardContent>
          </Card>

          {/* API Documentation */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5 text-primary" />
                API Documentation
              </CardTitle>
              <CardDescription>Integrate HoneyPot with your applications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h4 className="font-semibold mb-2">Send Incoming Message</h4>
                <code className="block p-3 bg-muted rounded-md text-sm">
                  POST /api/v1/messages/incoming
                </code>
                <p className="text-sm text-muted-foreground mt-2">
                  Submit a message to be analyzed for scam detection
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Get Intelligence</h4>
                <code className="block p-3 bg-muted rounded-md text-sm">
                  GET /api/v1/intelligence
                </code>
                <p className="text-sm text-muted-foreground mt-2">
                  Retrieve extracted scammer intelligence
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">List Conversations</h4>
                <code className="block p-3 bg-muted rounded-md text-sm">
                  GET /api/v1/conversations
                </code>
                <p className="text-sm text-muted-foreground mt-2">
                  Get all honeypot conversations
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Security Best Practices */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                Security Best Practices
              </CardTitle>
              <CardDescription>Keep your honeypot secure</CardDescription>
            </CardHeader>
            <CardContent className="prose prose-sm max-w-none dark:prose-invert">
              <ul>
                <li>Never expose your API keys in public repositories</li>
                <li>Use environment variables for sensitive configuration</li>
                <li>Regularly review and export intelligence data</li>
                <li>Keep your personas realistic but never use real personal information</li>
                <li>Monitor your dashboard for unusual activity</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
