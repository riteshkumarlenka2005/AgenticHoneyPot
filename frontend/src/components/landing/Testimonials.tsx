'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { GraduationCap, Shield, Search } from 'lucide-react'

const useCases = [
  {
    icon: Shield,
    title: 'Cybersecurity Research',
    description: 'Gather real-world scam data and patterns for security research and threat intelligence.',
    highlight: 'Research & Analysis',
  },
  {
    icon: Search,
    title: 'Law Enforcement',
    description: 'Collect evidence and intelligence on scammer operations to aid in investigations.',
    highlight: 'Investigation Support',
  },
  {
    icon: GraduationCap,
    title: 'Education & Training',
    description: 'Learn about scam tactics and train teams on identifying and handling cyber threats.',
    highlight: 'Training & Awareness',
  },
]

export function Testimonials() {
  return (
    <section className="py-20 sm:py-32 bg-background">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Use Cases
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            How organizations are using Agentic HoneyPot
          </p>
        </div>

        {/* Use Cases Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {useCases.map((useCase, index) => {
            const Icon = useCase.icon
            return (
              <Card key={index} className="relative overflow-hidden group hover:shadow-lg transition-shadow">
                <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -translate-y-16 translate-x-16 group-hover:scale-150 transition-transform"></div>
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="text-xs font-semibold text-primary mb-2">
                    {useCase.highlight}
                  </div>
                  <CardTitle className="text-xl">{useCase.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    {useCase.description}
                  </p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}
