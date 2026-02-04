'use client'

import { Shield, Bot, Database, Users, Zap, BarChart3 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const features = [
  {
    icon: Shield,
    title: 'Real-time Scam Detection',
    description: 'Advanced AI algorithms detect scam patterns instantly with high accuracy and confidence scoring.',
  },
  {
    icon: Bot,
    title: 'Autonomous AI Agents',
    description: 'Deploy intelligent agents that engage scammers automatically without human intervention.',
  },
  {
    icon: Database,
    title: 'Intelligence Extraction',
    description: 'Automatically extract and catalog scammer data including UPI IDs, bank accounts, and contact info.',
  },
  {
    icon: Users,
    title: 'Believable Personas',
    description: 'AI generates realistic personas that keep scammers engaged for maximum time waste and intelligence gathering.',
  },
  {
    icon: Zap,
    title: 'Mock Scammer Testing',
    description: 'Test your honeypot with built-in mock scammers to validate detection and engagement strategies.',
  },
  {
    icon: BarChart3,
    title: 'Analytics Dashboard',
    description: 'Comprehensive analytics on scam types, detection rates, intelligence gathered, and time wasted.',
  },
]

export function Features() {
  return (
    <section id="features" className="py-20 sm:py-32 bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Powerful Features
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Everything you need to detect, engage, and gather intelligence from scammers
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="border-2 hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
